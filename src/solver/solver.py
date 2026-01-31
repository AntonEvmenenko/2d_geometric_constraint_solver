from enum import Enum, auto
import itertools
from scipy.optimize import minimize
from solver.casadi_wrapper import casadi_minimize
from copy import copy
from constraints.constraints import CONSTRAINT_FUNCTION, CONSTRAINT_TYPE, Constraints
from geometry import Geometry
from geometric_primitives.point import Point, distance_p2p
from geometric_primitives.segment import Segment

class SOLVER_TYPE(Enum):
    SLSQP   = 0
    IPOPT   = 1

class SPECIAL_LINK(Enum):
    BASE    = -1
    ORPHAN  = -2
    FIXED   = -3

    def __repr__(self):
        return str(self.value)

class Solver:
    def __init__(self, geometry: Geometry, geometry_changed_callback, constraints):
        self.geometry = geometry
        self.geometry_changed_callback = geometry_changed_callback

        self.constraints: Constraints = constraints

        self.solver_type = SOLVER_TYPE.IPOPT

        self.degrees_of_freedom = 0

        self.is_solving = False

    def set_solver_type(self, solver_type):
        # print(f"Solver switched to: {solver_type.name}")
        self.solver_type = solver_type

    def get_base_id(self, id):
        temp = self.links[id]
        return id if isinstance(temp, SPECIAL_LINK) else temp

    def process_constraints_that_could_be_solved_by_substitution(self):
        points = list(itertools.chain.from_iterable([entity.points() for entity in (self.geometry.segments + self.geometry.arcs)]))

        self.point_to_id = {}
        self.values = []
        for i, point in enumerate(points):
            self.point_to_id[point] = i
            self.values += [point.x, point.y]

        self.number_of_primary_varialbes = len(self.values)
        self.links = [SPECIAL_LINK.BASE] * self.number_of_primary_varialbes

        def hv_helper(constraint, type):
            link = SPECIAL_LINK.BASE
            for point in constraint.entities:
                id = self.point_to_id[point] * 2 + (1 if type == CONSTRAINT_TYPE.HORIZONTALITY else 0)
                if self.links[id] != SPECIAL_LINK.BASE:
                    link = self.links[id]
                    break

            if link == SPECIAL_LINK.BASE:
                link = len(self.links)
                self.links.append(SPECIAL_LINK.BASE)

                for entity in constraint.entities:
                    if not entity is self.active_point:
                        self.values.append(entity.y if type == CONSTRAINT_TYPE.HORIZONTALITY else entity.x)
                        break

            for point in constraint.entities:
                id = self.point_to_id[point] * 2 + (1 if type == CONSTRAINT_TYPE.HORIZONTALITY else 0)

                existing_link = self.links[id]
                if existing_link != SPECIAL_LINK.BASE:
                    for i, _ in enumerate(self.links):
                        if self.links[i] == existing_link:
                            self.links[i] = link
                else:
                    self.links[id] = link

        for constraint in self.constraints:
            if constraint.type == CONSTRAINT_TYPE.COINCIDENCE:
                hv_helper(constraint, CONSTRAINT_TYPE.HORIZONTALITY)
                hv_helper(constraint, CONSTRAINT_TYPE.VERTICALITY)

            elif constraint.type == CONSTRAINT_TYPE.HORIZONTALITY:
                hv_helper(constraint, CONSTRAINT_TYPE.HORIZONTALITY)

            elif constraint.type == CONSTRAINT_TYPE.VERTICALITY:
                hv_helper(constraint, CONSTRAINT_TYPE.VERTICALITY)

        for constraint in self.constraints:
            if constraint.type == CONSTRAINT_TYPE.FIXED:
                for point in constraint.entities:
                    id = self.point_to_id[point]
                    id_x, id_y = id * 2, id * 2 + 1

                    self.links[self.get_base_id(id_x)] = SPECIAL_LINK.FIXED
                    self.links[self.get_base_id(id_y)] = SPECIAL_LINK.FIXED

        for constraint in self.constraints:
             for point in constraint.entities:
                if point is self.active_point:
                    id = self.point_to_id[point]
                    id_x, id_y = id * 2, id * 2 + 1
                    base_id_x, base_id_y = self.get_base_id(id_x), self.get_base_id(id_y)

                    if self.links[base_id_x] == SPECIAL_LINK.BASE:
                        self.values[base_id_x] = point.x

                    if self.links[base_id_y] == SPECIAL_LINK.BASE:
                        self.values[base_id_y] = point.y

        self.number_of_secondary_variables = len(self.links) - self.number_of_primary_varialbes

        orphan_vars = set(range(self.number_of_primary_varialbes, self.number_of_primary_varialbes + self.number_of_secondary_variables))

        for i in range(self.number_of_primary_varialbes):
            orphan_vars.discard(self.links[i])

        for i in orphan_vars:
            self.links[i] = SPECIAL_LINK.ORPHAN

        # print (f'links[{len(self.links)}]: {self.links}')

    def geometry_to_vars(self):
        vars = []

        for i, value in enumerate(self.values):
            if self.links[i] == SPECIAL_LINK.BASE:
                vars.append(value)

        for arc in self.geometry.arcs:
            vars.append(arc.d)

        return vars

    def geometry_from_vars(self, vars):
        vars_i = 0
        for i, _ in enumerate(self.values):
            if self.links[i] == SPECIAL_LINK.BASE:
                self.values[i] = vars[vars_i]
                vars_i += 1

        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                id = self.point_to_id[point]
                id_x, id_y = id * 2, id * 2 + 1

                temp = (SPECIAL_LINK.BASE, SPECIAL_LINK.FIXED)

                def helper(id):
                    if self.links[id] in temp:
                        return self.values[id]
                    if self.links[self.links[id]] in temp:
                        return self.values[self.links[id]]
                    return None

                x, y = helper(id_x), helper(id_y)

                point.x, point.y = point.x if x is None else x, point.y if y is None else y

        for arc in self.geometry.arcs:
            arc.d = vars[vars_i]
            vars_i += 1

    def f(self, x):
        self.geometry_from_vars(x)

        result = 0

        if not self.active_point is None:
            result = distance_p2p(self.active_point, self.active_point_copy) ** 2

        # print (f'f: {result}')

        return result

    def c(self, x):
        f = []

        self.geometry_from_vars(x)

        for constraint in self.constraints:
            # ignore all the constraints that do not depend on variables; it means they should be defined based on fixed points only
            if constraint in self.inactive_constraints:
                continue

            function = CONSTRAINT_FUNCTION[constraint.type]

            if function is None:
                continue

            f += function(*constraint. entities)

        # print (f'x: {x}')
        # print (f'c [{len(f)}]: {f}')
        # print (f'f: {f}')

        return f

    def detect_inactive_constraints(self):
        def is_fixed_entity(entity):
            if isinstance(entity, Point):
                id = self.point_to_id[entity]
                id_x, id_y = id * 2, id * 2 + 1
                return self.links[self.get_base_id(id_x)] == SPECIAL_LINK.FIXED and self.links[self.get_base_id(id_y)] == SPECIAL_LINK.FIXED
            elif isinstance(entity, Segment):
                return is_fixed_entity(entity.p1) and is_fixed_entity(entity.p2)
            else:
                return False

        inactive_constraints = set()

        for constraint in self.constraints:
            if constraint in inactive_constraints:
                continue
            if CONSTRAINT_FUNCTION[constraint.type] is None:
                continue
            if all(is_fixed_entity(entity) for entity in constraint.entities):
                inactive_constraints.add(constraint)

        return inactive_constraints

    def solve(self, active_point):
        if self.is_solving:
            return

        self.active_point = active_point
        self.active_point_copy = copy(active_point)

        self.process_constraints_that_could_be_solved_by_substitution()
        self.inactive_constraints = self.detect_inactive_constraints()

        self.constraints.inactive_constraints = len(self.inactive_constraints)
        self.constraints.solved_by_substitution_constraints = len(list(filter(lambda i: i.type in (CONSTRAINT_TYPE.COINCIDENCE, CONSTRAINT_TYPE.VERTICALITY, CONSTRAINT_TYPE.HORIZONTALITY), self.constraints)))
        self.constraints.fixed_constraints = len(list(filter(lambda i: i.type == CONSTRAINT_TYPE.FIXED, self.constraints)))

        initial_guess = self.geometry_to_vars()

        self.degrees_of_freedom = len(initial_guess)

        if self.degrees_of_freedom == 0:
            return

        # print (f'initial_guess[{len(initial_guess)}]: {initial_guess}')

        solution = None

        self.is_solving = True

        if self.solver_type == SOLVER_TYPE.SLSQP:
            solution = minimize(self.f, initial_guess, method = 'SLSQP', constraints = {'type' : 'eq', 'fun': self.c}, options = {'eps' : 1e-05})
            # print (solution)
        elif self.solver_type == SOLVER_TYPE.IPOPT:
            solution = casadi_minimize(self.f, initial_guess, constraints = {'type': 'eq', 'fun': self.c}, options = {'maxiter': 100, 'disp': False})
            self.geometry_from_vars(solution.x)

        self.is_solving = False

        self.geometry_changed_callback()
from scipy.optimize import minimize
from copy import copy
from constraints import COINCIDENCE, FIXED, constraint_function
from geometry import Geometry
from point import Point, distance_p2p
from arc import Arc

def point_to_vars(p: Point):
    return [p.x, p.y]

def point_from_vars(p: Point, vars):
    p.x, p.y = vars

class Solver:
    def __init__(self, geometry: Geometry, geometry_changed_callback, constraints):
        self.geometry = geometry
        self.geometry_changed_callback = geometry_changed_callback

        self.constraints = constraints

    def geometry_to_vars(self):
        vars = []
        processed_virtual_points = set()

        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                if (point in self.fixed_points):
                    continue
                elif (point in self.point_to_virtual_point):
                    virtual_point = self.point_to_virtual_point[point]

                    if (virtual_point in processed_virtual_points) or (virtual_point in self.fixed_points):
                        continue

                    vars += point_to_vars(virtual_point)
                    processed_virtual_points.add(virtual_point)
                else:
                    vars += point_to_vars(point)

        return vars

    def geometry_from_vars(self, vars):
        position = 0

        processed_virtual_points = set()

        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                if (point in self.fixed_points):
                    continue
                elif (point in self.point_to_virtual_point):
                    virtual_point = self.point_to_virtual_point[point]

                    point.x, point.y = virtual_point.x, virtual_point.y

                    if (virtual_point in self.fixed_points) or (virtual_point in processed_virtual_points):
                        continue

                    vars_length = len(point_to_vars(virtual_point))
                    point_from_vars(virtual_point, vars[position : position + vars_length])
                    point.x, point.y = virtual_point.x, virtual_point.y
                    position += vars_length
                    processed_virtual_points.add(virtual_point)
                else:
                    vars_length = len(point_to_vars(point))
                    point_from_vars(point, vars[position : position + vars_length])
                    position += vars_length
        for arc in self.geometry.arcs:
            arc.update_center()

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
            function = constraint_function[constraint.type]

            if not function is None:
                f += function(*constraint.entities)

        # print (f'c: {f}')

        return f

    def create_virtual_points(self):
        self.point_to_virtual_point = {}

        for constraint in self.constraints:
            if constraint.type == COINCIDENCE:
                virtual_point = Point(constraint.entities[0].x, constraint.entities[0].y)

                for point in constraint.entities:
                    if point in self.point_to_virtual_point:
                        virtual_point = self.point_to_virtual_point[point]
                        break

                for point in constraint.entities:
                    self.point_to_virtual_point[point] = virtual_point

                if point is self.active_point:
                    virtual_point.x, virtual_point.y = point.x, point.y

    def create_fixed_points(self):
        self.fixed_points = set()

        for constraint in self.constraints:
            if constraint.type == FIXED:
                # point = constraint.entities[0]
                for point in constraint.entities:
                    if point in self.point_to_virtual_point:
                        virtual_point = self.point_to_virtual_point[point]
                        self.fixed_points.add(virtual_point)
                    else:
                        self.fixed_points.add(point)

    def solve(self, active_point):
        self.active_point = active_point
        self.active_point_copy = copy(active_point)

        self.create_virtual_points()
        self.create_fixed_points()

        initial_guess = self.geometry_to_vars()

        # print (f'initial_guess ({len(initial_guess)}) = {initial_guess}')

        solution = minimize(self.f, initial_guess, method = 'SLSQP', constraints = {'type' : 'eq', 'fun': self.c})

        # print (solution)

        self.geometry_changed_callback()
from collections import Counter
from enum import Enum, auto
from constraints.constraint import Constraint
from constraints.constraint_equations import *
from geometric_primitives.point import Point
from geometric_primitives.segment import Segment
from geometric_primitives.arc import Arc

class CONSTRAINT_TYPE(Enum):
    COINCIDENCE             = auto()
    PARALLELITY             = auto()
    PERPENDICULARITY        = auto()
    EQUAL_LENGTH_OR_RADIUS  = auto()
    FIXED                   = auto()
    HORIZONTALITY           = auto()
    VERTICALITY             = auto()
    TANGENCY                = auto()
    CONCENTRICITY           = auto()
    LENGTH                  = auto()

class QUANTITY(Enum):
    ONE             = auto()
    TWO             = auto()
    MORE_THAN_ZERO  = auto()
    MORE_THAN_ONE   = auto()

CONSTRAINT_REQUIREMENT = {
    CONSTRAINT_TYPE.COINCIDENCE:                [[QUANTITY.MORE_THAN_ONE, Point]],
    CONSTRAINT_TYPE.PARALLELITY:                [[Segment, Segment]],
    CONSTRAINT_TYPE.PERPENDICULARITY:           [[Segment, Segment]],
    CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS:     [[Segment, Segment], [Arc, Arc]],
    CONSTRAINT_TYPE.FIXED:                      [[Point]],
    CONSTRAINT_TYPE.HORIZONTALITY:              [[Segment], [Point, Point]],
    CONSTRAINT_TYPE.VERTICALITY:                [[Segment], [Point, Point]],
    CONSTRAINT_TYPE.TANGENCY:                   [[Arc, Segment], [Arc, Arc]],
    CONSTRAINT_TYPE.CONCENTRICITY:              [[Arc, Arc]],
    CONSTRAINT_TYPE.LENGTH:                     [[Segment, int], [Arc, int]],
}

SPLITTABLE_CONSTRAINTS = [
    CONSTRAINT_TYPE.PARALLELITY,
    CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS,
    CONSTRAINT_TYPE.FIXED,
    CONSTRAINT_TYPE.HORIZONTALITY,
    CONSTRAINT_TYPE.VERTICALITY,
    CONSTRAINT_TYPE.TANGENCY,
    CONSTRAINT_TYPE.CONCENTRICITY,
]

CONSTRAINT_FUNCTION = {
    CONSTRAINT_TYPE.COINCIDENCE:               None,
    CONSTRAINT_TYPE.PARALLELITY:               parallel,
    CONSTRAINT_TYPE.PERPENDICULARITY:          perpendicular,
    CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS:    equal_length_or_radius,
    CONSTRAINT_TYPE.FIXED:                     None,
    CONSTRAINT_TYPE.HORIZONTALITY:             None,
    CONSTRAINT_TYPE.VERTICALITY:               None,
    CONSTRAINT_TYPE.TANGENCY:                  tangency,
    CONSTRAINT_TYPE.CONCENTRICITY:             concentricity,
    CONSTRAINT_TYPE.LENGTH:                    length,
}

class Constraints(list):
    def __init__(self, *args):
        list.__init__(self, *args)

        self.inactive_constraints = 0
        self.solved_by_substitution_constraints = 0
        self.fixed_constraints = 0

    def add_constraint(self, type, entities):
        new_constraints = []

        if type in SPLITTABLE_CONSTRAINTS:
            for constraint_requirement in CONSTRAINT_REQUIREMENT.get(type, ()):
                if Constraints.check_constraint_applicability(type, constraint_requirement, entities):
                    split_len = len(constraint_requirement)
                    assert split_len in (1, 2)
                    if split_len == 1:
                        for entity in entities:
                            new_constraints.append(Constraint([entity], type))
                    elif split_len == 2:
                        for pair in pairs(entities):
                            new_constraints.append(Constraint((pair[0], pair[1]), type))
        else:
            new_constraints.append(Constraint(entities, type))

        self += new_constraints
        return new_constraints

    def get_useless_constraints(self, entities_to_be_removed):
        useless_constraints = set()

        for constraint in self:
            if not constraint.type in Constraints.get_available_constraints(set(constraint.entities) - set(entities_to_be_removed)):
                useless_constraints.add(constraint)

        return useless_constraints

    @staticmethod
    def check_constraint_applicability(constraint_type, constraint_requirement, entities):
        counter_entities = Counter([i.__class__ for i in entities])
        counter_constraint_requirement = Counter(constraint_requirement)

        if QUANTITY.MORE_THAN_ONE in constraint_requirement and len(counter_entities) == 1:
            count = len([entity for entity in entities if entity.__class__ in constraint_requirement])
            all_entities = count == len(entities)

            if all_entities and count > 1:
                return True
        elif (counter_entities == counter_constraint_requirement):
            return True
        elif constraint_type in SPLITTABLE_CONSTRAINTS and len(counter_entities) == 1 \
            and counter_entities.keys() == counter_constraint_requirement.keys() and len(entities) >= len(constraint_requirement):
            return True

        return False

    @staticmethod
    def get_available_constraints(entities):
        available_constraints = set()

        for constraint_type in CONSTRAINT_TYPE:
            for constraint_requirement in CONSTRAINT_REQUIREMENT.get(constraint_type, ()):
                if Constraints.check_constraint_applicability(constraint_type, constraint_requirement, entities):
                    available_constraints.add(constraint_type)

        return available_constraints
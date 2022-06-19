from collections import Counter
from enum import Enum, auto
from constraints.constraint import Constraint
from geometric_primitives.point import Point, distance_p2p
from geometric_primitives.segment import Segment
from geometric_primitives.arc import Arc
from geometric_primitives.line import Line, distance_p2l
from geometric_primitives.vector import Vector, cross, dot

class Constraints(list):
    def __init__(self, *args):
        list.__init__(self, *args)

        self.inactive_constraints = 0
        self.solved_by_substitution_constraints = 0
        self.fixed_constraints = 0

class CONSTRAINT_TYPES(Enum):
    COINCIDENCE             = auto()
    PARALLELITY             = auto()
    PERPENDICULARITY        = auto()
    EQUAL_LENGTH_OR_RADIUS  = auto()
    LENGTH                  = auto()
    FIXED                   = auto()
    HORIZONTALITY           = auto()
    VERTICALITY             = auto()
    TANGENCY                = auto()
    CONCENTRICITY           = auto()

# helpers

def pairs(entities):
    return zip(entities[:-1], entities[1:])

def all_entities(entities, cls):
    return all(entity.__class__ is cls for entity in entities)

# constraints

def parallel(s1: Segment, s2: Segment):
    return [cross(s1.vector(), s2.vector())]

def perpendicular(s1: Segment, s2: Segment):
    return [dot(s1.vector(), s2.vector())]

def equal_length_or_radius(entity1, entity2):
    entities = (entity1, entity2)
    segments, arcs = all_entities(entities, Segment), all_entities(entities, Arc)
    assert segments or arcs
    return [entity1.length() - entity2.length()] if segments else [entity1.radius() - entity2.radius()]

def length(segment: Segment, length: float):
    return [(Vector(segment.p2.x - segment.p1.x, segment.p2.y - segment.p1.y).length() - length)]

def tangency(entity1, entity2):
    temp = Counter((entity1.__class__, entity2.__class__))
    if temp == Counter((Arc, Segment)):
        arc = entity1 if isinstance(entity1, Arc) else entity2
        segment = entity1 if isinstance(entity1, Segment) else entity2
        return [distance_p2l(arc.center(), Line(segment.p1, segment.p2)) - arc.radius()]
    elif temp == Counter((Arc, Arc)):
        return [distance_p2p(entity1.center(), entity2.center()) - (entity1.radius() + entity2.radius())]
    else:
        assert False

def concentricity(arc1: Arc, arc2: Arc):
    return [distance_p2p(arc1.center(), arc2.center())]

CONSTRAINT_FUNCTION = {
    CONSTRAINT_TYPES.COINCIDENCE:               None,
    CONSTRAINT_TYPES.PARALLELITY:               parallel,
    CONSTRAINT_TYPES.PERPENDICULARITY:          perpendicular,
    CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS:    equal_length_or_radius,
    CONSTRAINT_TYPES.LENGTH:                    length,
    CONSTRAINT_TYPES.FIXED:                     None,
    CONSTRAINT_TYPES.HORIZONTALITY:             None,
    CONSTRAINT_TYPES.VERTICALITY:               None,
    CONSTRAINT_TYPES.TANGENCY:                  tangency,
    CONSTRAINT_TYPES.CONCENTRICITY:             concentricity,
}

class QUANTITY(Enum):
    ONE             = auto()
    TWO             = auto()
    MORE_THAN_ZERO  = auto()
    MORE_THAN_ONE   = auto()

CONSTRAINT_REQUIREMENTS = {
    CONSTRAINT_TYPES.COINCIDENCE:               [[QUANTITY.MORE_THAN_ONE, Point]],
    CONSTRAINT_TYPES.PARALLELITY:               [[Segment, Segment]],
    CONSTRAINT_TYPES.PERPENDICULARITY:          [[Segment, Segment]],
    CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS:    [[Segment, Segment], [Arc, Arc]],
    # constraint_types.LENGTH:                  (),
    CONSTRAINT_TYPES.FIXED:                     [[Point]],
    CONSTRAINT_TYPES.HORIZONTALITY:             [[Point, Point]],
    CONSTRAINT_TYPES.VERTICALITY:               [[Point, Point]],
    CONSTRAINT_TYPES.TANGENCY:                  [[Arc, Segment], [Arc, Arc]],
    CONSTRAINT_TYPES.CONCENTRICITY:             [[Arc, Arc]],
}

SPLITTABLE_CONSTRAINTS = [
    CONSTRAINT_TYPES.PARALLELITY,
    CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS,
    CONSTRAINT_TYPES.FIXED,
    CONSTRAINT_TYPES.HORIZONTALITY,
    CONSTRAINT_TYPES.VERTICALITY,
    CONSTRAINT_TYPES.TANGENCY,
    CONSTRAINT_TYPES.CONCENTRICITY,
]

def check_constraint_applicability(constraint_type, constraint_requirement, entities, counter_entities = None):
    if counter_entities is None:
        counter_entities = Counter([i.__class__ for i in entities])

    counter_constraint_requirement = Counter(constraint_requirement)
    if QUANTITY.MORE_THAN_ONE in constraint_requirement and len(counter_entities) == 1:
        count = len([entity for entity in entities if entity.__class__ in constraint_requirement])
        right_count = count > 1
        all_entities = count == len(entities)

        if right_count and all_entities:
            return True
    elif (counter_entities == counter_constraint_requirement):
        return True
    elif constraint_type in SPLITTABLE_CONSTRAINTS and len(counter_entities) == 1 \
        and counter_entities.keys() == counter_constraint_requirement.keys() and len(entities) >= len(constraint_requirement):
        return True

    return False

def get_available_constraints(entities):
    available_constraints = set()

    counter_entities = Counter([i.__class__ for i in entities])

    for constraint_type in CONSTRAINT_TYPES:
        for constraint_requirement in CONSTRAINT_REQUIREMENTS.get(constraint_type, ()):
            if check_constraint_applicability(constraint_type, constraint_requirement, entities, counter_entities):
                available_constraints.add(constraint_type)

    return available_constraints

def get_useless_constraints(constraints, entities_to_be_removed):
    useless_constraints = set()

    for constraint in constraints:
        if not constraint.type in get_available_constraints(set(constraint.entities) - set(entities_to_be_removed)):
            useless_constraints.add(constraint)

    return useless_constraints

def add_constraint(constraints, type, entities):
    new_constraints = []

    if type in SPLITTABLE_CONSTRAINTS:
        for constraint_requirement in CONSTRAINT_REQUIREMENTS.get(type, ()):
            if check_constraint_applicability(type, constraint_requirement, entities):
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

    constraints += new_constraints
    return new_constraints
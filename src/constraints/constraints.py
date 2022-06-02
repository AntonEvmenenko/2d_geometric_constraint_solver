from collections import Counter
from enum import Enum, auto
from geometric_primitives.point import Point, distance_p2p
from geometric_primitives.segment import Segment
from geometric_primitives.arc import Arc
from geometric_primitives.line import Line, distance_p2l
from geometric_primitives.vector import Vector, cross, dot

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

def parallel(*segments):
    return [cross(pair[0].vector(), pair[1].vector()) for pair in pairs(segments)]

def perpendicular(s1: Segment, s2: Segment):
    return [dot(s1.vector(), s2.vector())]

def equal_length_or_radius(*entities):
    segments, arcs = all_entities(entities, Segment), all_entities(entities, Arc)
    assert segments or arcs
    return [(pair[0].length() - pair[1].length()) for pair in pairs(entities)] if segments else [(pair[0].radius() - pair[1].radius()) for pair in pairs(entities)]

def length(segment: Segment, length: float):
    return [(Vector(segment.p2.x - segment.p1.x, segment.p2.y - segment.p1.y).length() - length)]

def horizontality(*entities):
    points, segments = all_entities(entities, Point), all_entities(entities, Segment)
    assert points or segments
    return [(pair[0].y - pair[1].y) for pair in pairs(entities)] if points else [(segment.p1.y - segment.p2.y) for segment in entities]

def verticality(*entities):
    points, segments = all_entities(entities, Point), all_entities(entities, Segment)
    assert points or segments
    return [(pair[0].x - pair[1].x) for pair in pairs(entities)] if points else [(segment.p1.x - segment.p2.x) for segment in entities]

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

def concentricity(arc1, arc2):
    return [distance_p2p(arc1.center(), arc2.center())]

CONSTRAINT_FUNCTION = {
    CONSTRAINT_TYPES.COINCIDENCE:               None,
    CONSTRAINT_TYPES.PARALLELITY:               parallel,
    CONSTRAINT_TYPES.PERPENDICULARITY:          perpendicular,
    CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS:    equal_length_or_radius,
    CONSTRAINT_TYPES.LENGTH:                    length,
    CONSTRAINT_TYPES.FIXED:                     None,
    CONSTRAINT_TYPES.HORIZONTALITY:             horizontality,
    CONSTRAINT_TYPES.VERTICALITY:               verticality,
    CONSTRAINT_TYPES.TANGENCY:                  tangency,
    CONSTRAINT_TYPES.CONCENTRICITY:             concentricity,
}

class QUANTITY(Enum):
    MORE_THAN_ZERO  = auto()
    MORE_THAN_ONE   = auto()

CONSTRAINT_REQUIREMENTS = {
    CONSTRAINT_TYPES.COINCIDENCE:               [(QUANTITY.MORE_THAN_ONE, Point)],
    CONSTRAINT_TYPES.PARALLELITY:               [(QUANTITY.MORE_THAN_ONE, Segment)],
    CONSTRAINT_TYPES.PERPENDICULARITY:          [(Segment, Segment)],
    CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS:    [(QUANTITY.MORE_THAN_ONE, Segment), (QUANTITY.MORE_THAN_ONE, Arc)],
    # constraint_types.LENGTH:                  (),
    CONSTRAINT_TYPES.FIXED:                     [(QUANTITY.MORE_THAN_ZERO, Point)],
    CONSTRAINT_TYPES.HORIZONTALITY:             [(QUANTITY.MORE_THAN_ZERO, Segment), (QUANTITY.MORE_THAN_ONE, Point)],
    CONSTRAINT_TYPES.VERTICALITY:               [(QUANTITY.MORE_THAN_ZERO, Segment), (QUANTITY.MORE_THAN_ONE, Point)],
    CONSTRAINT_TYPES.TANGENCY:                  [(Arc, Segment), (Arc, Arc)],
    CONSTRAINT_TYPES.CONCENTRICITY:             [(Arc, Arc)]
}

def get_available_constraints(entities):
    available_constraints = set()

    for constraint_type in CONSTRAINT_TYPES:
        for constraint_requirement in CONSTRAINT_REQUIREMENTS.get(constraint_type, ()):
            if (QUANTITY.MORE_THAN_ZERO in constraint_requirement) or (QUANTITY.MORE_THAN_ONE in constraint_requirement):
                count = len([entity for entity in entities if entity.__class__ in constraint_requirement])
                right_count = (QUANTITY.MORE_THAN_ONE in constraint_requirement and count > 1) or (QUANTITY.MORE_THAN_ZERO in constraint_requirement and count > 0)
                all_entities = count == len(entities)

                if right_count and all_entities:
                    available_constraints.add(constraint_type)
            elif (Counter([i.__class__ for i in entities]) == Counter(constraint_requirement)):
                available_constraints.add(constraint_type)

    return available_constraints

def get_useless_constraints(constraints, entities_to_be_removed):
    useless_constraints = set()

    for constraint in constraints:
        if not constraint.type in get_available_constraints(set(constraint.entities) - set(entities_to_be_removed)):
            useless_constraints.add(constraint)

    return useless_constraints
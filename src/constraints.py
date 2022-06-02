from collections import Counter
from enum import Enum, auto
from tkinter import ARC
from point import Point, distance_p2p
from segment import Segment
from arc import Arc
from line import Line, distance_p2l
from vector import Vector, cross, dot

class constraint_types(Enum):
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

constraint_function = {
    constraint_types.COINCIDENCE:            None,
    constraint_types.PARALLELITY:            parallel,
    constraint_types.PERPENDICULARITY:       perpendicular,
    constraint_types.EQUAL_LENGTH_OR_RADIUS: equal_length_or_radius,
    constraint_types.LENGTH:                 length,
    constraint_types.FIXED:                  None,
    constraint_types.HORIZONTALITY:          horizontality,
    constraint_types.VERTICALITY:            verticality,
    constraint_types.TANGENCY:               tangency,
}

class quantity(Enum):
    MORE_THAN_ZERO  = auto()
    MORE_THAN_ONE   = auto()

constraint_requirements = {
    constraint_types.COINCIDENCE:            [(quantity.MORE_THAN_ONE, Point)],
    constraint_types.PARALLELITY:            [(quantity.MORE_THAN_ONE, Segment)],
    constraint_types.PERPENDICULARITY:       [(Segment, Segment)],
    constraint_types.EQUAL_LENGTH_OR_RADIUS: [(quantity.MORE_THAN_ONE, Segment), (quantity.MORE_THAN_ONE, Arc)],
    # constraint_types.LENGTH:               (),
    constraint_types.FIXED:                  [(quantity.MORE_THAN_ZERO, Point)],
    constraint_types.HORIZONTALITY:          [(quantity.MORE_THAN_ZERO, Segment), (quantity.MORE_THAN_ONE, Point)],
    constraint_types.VERTICALITY:            [(quantity.MORE_THAN_ZERO, Segment), (quantity.MORE_THAN_ONE, Point)],
    constraint_types.TANGENCY:               [(Arc, Segment), (Arc, Arc)]
}

def get_available_constraints(entities):
    available_constraints = set()

    for constraint_type in constraint_types:
        for constraint_requirement in constraint_requirements.get(constraint_type, ()):
            if (quantity.MORE_THAN_ZERO in constraint_requirement) or (quantity.MORE_THAN_ONE in constraint_requirement):
                count = len([entity for entity in entities if entity.__class__ in constraint_requirement])
                right_count = (quantity.MORE_THAN_ONE in constraint_requirement and count > 1) or (quantity.MORE_THAN_ZERO in constraint_requirement and count > 0)
                all_entities = count == len(entities)

                if right_count and all_entities:
                    available_constraints.add(constraint_type)
            elif (Counter([i.__class__ for i in entities]) == Counter(constraint_requirement)):
                available_constraints.add(constraint_type)

    return available_constraints
from collections import Counter
from point import Point
from segment import Segment
from vector import Vector, cross, dot

COINCIDENCE         = 0
PARALLELITY         = 1
PERPENDICULARITY    = 2
EQUAL_LENGTH        = 3
LENGTH              = 4
FIXED               = 5
HORIZONTALITY       = 6
VERTICALITY         = 7
TANGENCY            = 8
CONCENTRICITY       = 9

constraint_types = [
    COINCIDENCE,
    PARALLELITY,
    PERPENDICULARITY,
    EQUAL_LENGTH,
    # LENGTH,
    FIXED,
    HORIZONTALITY,
    VERTICALITY,
]

def parallel(*segments):
    return [cross(pair[0].vector(), pair[1].vector()) for pair in zip(segments[:-1], segments[1:])]

def perpendicular(s1: Segment, s2: Segment):
    return [dot(s1.vector(), s2.vector())]

def equal_length(*segments):
    return [(pair[0].vector().length() - pair[1].vector().length()) for pair in zip(segments[:-1], segments[1:])]

def length(segment: Segment, length: float):
    return [(Vector(segment.p2.x - segment.p1.x, segment.p2.y - segment.p1.y).length() - length)]

def horizontality(*entities):
    points = all(entity.__class__ is Point for entity in entities)
    segments = all(entity.__class__ is Segment for entity in entities)
    assert points or segments
    return [(pair[0].y - pair[1].y) for pair in zip(entities[:-1], entities[1:])] if points else [(segment.p1.y - segment.p2.y) for segment in entities]

def verticality(*entities):
    points = all(entity.__class__ is Point for entity in entities)
    segments = all(entity.__class__ is Segment for entity in entities)
    assert points or segments
    return [(pair[0].x - pair[1].x) for pair in zip(entities[:-1], entities[1:])] if points else [(segment.p1.x - segment.p2.x) for segment in entities]

constraint_function = {
    COINCIDENCE:        None,
    PARALLELITY:        parallel,
    PERPENDICULARITY:   perpendicular,
    EQUAL_LENGTH:       equal_length,
    LENGTH:             length,
    FIXED:              None,
    HORIZONTALITY:      horizontality,
    VERTICALITY:        verticality,
}

MORE_THAN_ZERO  = 10000
MORE_THAN_ONE   = 10001

constraint_requirements = {
    COINCIDENCE:        [(MORE_THAN_ONE, Point)],
    PARALLELITY:        [(MORE_THAN_ONE, Segment)],
    PERPENDICULARITY:   [(Segment, Segment)],
    EQUAL_LENGTH:       [(MORE_THAN_ONE, Segment)],
    # LENGTH:             (),
    FIXED:              [(MORE_THAN_ZERO, Point)],
    HORIZONTALITY:      [(MORE_THAN_ZERO, Segment), (MORE_THAN_ONE, Point)],
    VERTICALITY:        [(MORE_THAN_ZERO, Segment), (MORE_THAN_ONE, Point)],
}

def get_available_constraints(entities):
    available_constraints = set()

    for constraint_type in constraint_types:
        for constraint_requirement in constraint_requirements[constraint_type]:
            if (MORE_THAN_ZERO in constraint_requirement) or (MORE_THAN_ONE in constraint_requirement):
                count = len([entity for entity in entities if entity.__class__ in constraint_requirement])
                right_count = (MORE_THAN_ONE in constraint_requirement and count > 1) or (MORE_THAN_ZERO in constraint_requirement and count > 0)
                all_entities = count == len(entities)

                if right_count and all_entities:
                    available_constraints.add(constraint_type)
            elif (Counter([i.__class__ for i in entities]) == Counter(constraint_requirement)):
                available_constraints.add(constraint_type)

    return available_constraints
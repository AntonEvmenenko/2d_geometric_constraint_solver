from collections import Counter
from tkinter import ARC
from point import Point, distance_p2p
from segment import Segment
from arc import Arc
from line import Line, distance_p2l
from vector import Vector, cross, dot

COINCIDENCE             = 0
PARALLELITY             = 1
PERPENDICULARITY        = 2
EQUAL_LENGTH_OR_RADIUS  = 3
LENGTH                  = 4
FIXED                   = 5
HORIZONTALITY           = 6
VERTICALITY             = 7
TANGENCY                = 8
CONCENTRICITY           = 9

constraint_types = [
    COINCIDENCE,
    PARALLELITY,
    PERPENDICULARITY,
    EQUAL_LENGTH_OR_RADIUS,
    # LENGTH,
    FIXED,
    HORIZONTALITY,
    VERTICALITY,
    TANGENCY,
]

def parallel(*segments):
    return [cross(pair[0].vector(), pair[1].vector()) for pair in zip(segments[:-1], segments[1:])]

def perpendicular(s1: Segment, s2: Segment):
    return [dot(s1.vector(), s2.vector())]

def equal_length_or_radius(*entities):
    segments = all(entity.__class__ is Segment for entity in entities)
    arcs = all(entity.__class__ is Arc for entity in entities)
    assert segments or arcs
    return [(pair[0].vector().length() - pair[1].vector().length()) for pair in zip(entities[:-1], entities[1:])] if segments else \
        [(pair[0].radius() - pair[1].radius()) for pair in zip(entities[:-1], entities[1:])]

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
    COINCIDENCE:            None,
    PARALLELITY:            parallel,
    PERPENDICULARITY:       perpendicular,
    EQUAL_LENGTH_OR_RADIUS: equal_length_or_radius,
    LENGTH:                 length,
    FIXED:                  None,
    HORIZONTALITY:          horizontality,
    VERTICALITY:            verticality,
    TANGENCY:               tangency,
}

MORE_THAN_ZERO  = 10000
MORE_THAN_ONE   = 10001

constraint_requirements = {
    COINCIDENCE:            [(MORE_THAN_ONE, Point)],
    PARALLELITY:            [(MORE_THAN_ONE, Segment)],
    PERPENDICULARITY:       [(Segment, Segment)],
    EQUAL_LENGTH_OR_RADIUS: [(MORE_THAN_ONE, Segment), (MORE_THAN_ONE, Arc)],
    # LENGTH:               (),
    FIXED:                  [(MORE_THAN_ZERO, Point)],
    HORIZONTALITY:          [(MORE_THAN_ZERO, Segment), (MORE_THAN_ONE, Point)],
    VERTICALITY:            [(MORE_THAN_ZERO, Segment), (MORE_THAN_ONE, Point)],
    TANGENCY:               [(Arc, Segment), (Arc, Arc)]
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
from segment import Segment
from vector import Vector, cross, dot

COINCIDENCE     = 0
PARALLEL        = 1
PERPENDICULAR   = 2
EQUAL_LENGTH    = 3
LENGTH          = 4
FIXED           = 5
HORIZONTALITY   = 6
VERTICALITY     = 7

def parallel(s1: Segment, s2: Segment):
    return [cross(s1.vector(), s2.vector())]

def perpendicular(s1: Segment, s2: Segment):
    return [dot(s1.vector(), s2.vector())]

def equal_length(s1: Segment, s2: Segment):
    return [s1.vector().length() - s2.vector().length()]

def length(segment: Segment, length: float):
    return [(Vector(segment.p2.x - segment.p1.x, segment.p2.y - segment.p1.y).length() - length)]

def horizontality(s: Segment):
    return [s.p1.y - s.p2.y]

def verticality(s: Segment):
    return [s.p1.x - s.p2.x]

constraint_function = {
    COINCIDENCE:    None,
    PARALLEL:       parallel,
    PERPENDICULAR:  perpendicular,
    EQUAL_LENGTH:   equal_length,
    LENGTH:         length,
    FIXED:          None,
    HORIZONTALITY:  horizontality,
    VERTICALITY:    verticality,
}
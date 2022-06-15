from constraints.constraint import Constraint
from constraints.constraints import CONSTRAINT_TYPES
from geometric_primitives.point import Point
from geometric_primitives.segment import Segment
from geometric_primitives.arc import Arc

SCALE = 1

def clear_geometry_and_constraints(geometry, constraints):
    geometry.clear()
    constraints.clear()

def Lines(geometry, constraints):
    clear_geometry_and_constraints(geometry, constraints)

    geometry.segments = [
        Segment(Point(300 * SCALE, 300 * SCALE), Point(500 * SCALE, 300 * SCALE)),
        Segment(Point(500 * SCALE, 300 * SCALE), Point(400 * SCALE, 200 * SCALE)),
        Segment(Point(400 * SCALE, 200 * SCALE), Point(300 * SCALE, 300 * SCALE)),
        
        Segment(Point(500 * SCALE, 300 * SCALE), Point(600 * SCALE, 250 * SCALE)),
        Segment(Point(600 * SCALE, 250 * SCALE), Point(400 * SCALE, 200 * SCALE)),
    ]

    constraints += [
        Constraint([geometry.segments[0].p1, geometry.segments[2].p2], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], CONSTRAINT_TYPES.COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[3].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[3].p2, geometry.segments[4].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[4].p2, geometry.segments[1].p2], CONSTRAINT_TYPES.COINCIDENCE),

        Constraint([geometry.segments[1], geometry.segments[2]], CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS),
        Constraint([geometry.segments[3], geometry.segments[4]], CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS),
        Constraint([geometry.segments[3], geometry.segments[1]], CONSTRAINT_TYPES.EQUAL_LENGTH_OR_RADIUS),

        Constraint([geometry.segments[0].p1], CONSTRAINT_TYPES.FIXED),
        Constraint([geometry.segments[0].p2], CONSTRAINT_TYPES.FIXED),
    ]

def CutSlot(geometry, constraints):
    clear_geometry_and_constraints(geometry, constraints)

    geometry.segments = [
        Segment(Point(300 * SCALE, 200 * SCALE), Point(300 * SCALE, 400 * SCALE)),
        Segment(Point(300 * SCALE, 400 * SCALE), Point(500 * SCALE, 400 * SCALE)),
        Segment(Point(500 * SCALE, 400 * SCALE), Point(500 * SCALE, 200 * SCALE)),
    ]

    geometry.arcs = [
        Arc(Point(300 * SCALE, 200 * SCALE), Point(500 * SCALE, 200 * SCALE), Point(400 * SCALE, 100 * SCALE))
    ]

    constraints += [
        Constraint([geometry.segments[0], geometry.arcs[0]], CONSTRAINT_TYPES.TANGENCY),
        Constraint([geometry.segments[2], geometry.arcs[0]], CONSTRAINT_TYPES.TANGENCY),

        Constraint([geometry.segments[0].p1, geometry.arcs[0].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[2].p2, geometry.arcs[0].p2], CONSTRAINT_TYPES.COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], CONSTRAINT_TYPES.COINCIDENCE),
    ]

def Slot(geometry, constraints):
    clear_geometry_and_constraints(geometry, constraints)

    geometry.segments = [
        Segment(Point(300 * SCALE, 200 * SCALE), Point(300 * SCALE, 400 * SCALE)),
        Segment(Point(500 * SCALE, 400 * SCALE), Point(500 * SCALE, 200 * SCALE)),
    ]

    geometry.arcs = [
        Arc(Point(300 * SCALE, 200 * SCALE), Point(500 * SCALE, 200 * SCALE), Point(400 * SCALE, 100 * SCALE)),
        Arc(Point(500 * SCALE, 400 * SCALE), Point(300 * SCALE, 400 * SCALE), Point(400 * SCALE, 500 * SCALE)),
    ]

    constraints += [
        Constraint([geometry.segments[0], geometry.arcs[0]], CONSTRAINT_TYPES.TANGENCY),
        Constraint([geometry.segments[0], geometry.arcs[1]], CONSTRAINT_TYPES.TANGENCY),
        Constraint([geometry.segments[1], geometry.arcs[0]], CONSTRAINT_TYPES.TANGENCY),
        Constraint([geometry.segments[1], geometry.arcs[1]], CONSTRAINT_TYPES.TANGENCY),

        Constraint([geometry.segments[0].p1, geometry.arcs[0].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.arcs[1].p2], CONSTRAINT_TYPES.COINCIDENCE),

        Constraint([geometry.segments[1].p1, geometry.arcs[1].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.arcs[0].p2], CONSTRAINT_TYPES.COINCIDENCE),
    ]

def Rect(geometry, constraints):
    clear_geometry_and_constraints(geometry, constraints)

    geometry.segments = [
        Segment(Point(300 * SCALE, 300 * SCALE), Point(500 * SCALE, 300 * SCALE)),
        Segment(Point(500 * SCALE, 300 * SCALE), Point(500 * SCALE, 500 * SCALE)),
        Segment(Point(500 * SCALE, 500 * SCALE), Point(300 * SCALE, 500 * SCALE)),
        Segment(Point(300 * SCALE, 500 * SCALE), Point(300 * SCALE, 300 * SCALE)),
    ]

    constraints += [
        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[2].p2, geometry.segments[3].p1], CONSTRAINT_TYPES.COINCIDENCE),
        Constraint([geometry.segments[3].p2, geometry.segments[0].p1], CONSTRAINT_TYPES.COINCIDENCE),
    ]

examples = [
    Lines,
    CutSlot,
    Slot,
    Rect,
]
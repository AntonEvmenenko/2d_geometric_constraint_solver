from constraint import Constraint
from constraints import CONSTRAINT_TYPES
from point import Point
from segment import Segment
from arc import Arc

def clear_geometry_and_constraints(geometry, constraints):
    geometry.clear()
    constraints.clear()

def Lines(geometry, constraints):
    clear_geometry_and_constraints(geometry, constraints)

    geometry.segments = [
        Segment(Point(300, 300), Point(500, 300)),
        Segment(Point(500, 300), Point(400, 200)),
        Segment(Point(400, 200), Point(300, 300)),
        
        Segment(Point(500, 300), Point(600, 250)),
        Segment(Point(600, 250), Point(400, 200)),
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
        Segment(Point(300, 200), Point(300, 400)),
        Segment(Point(300, 400), Point(500, 400)),
        Segment(Point(500, 400), Point(500, 200)),
    ]

    geometry.arcs = [
        Arc(Point(300, 200), Point(500, 200), Point(400, 100))
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
        Segment(Point(300, 200), Point(300, 400)),
        Segment(Point(500, 400), Point(500, 200)),
    ]

    geometry.arcs = [
        Arc(Point(300, 200), Point(500, 200), Point(400, 100)),
        Arc(Point(500, 400), Point(300, 400), Point(400, 500)),
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

examples = [
    Lines,
    CutSlot,
    Slot,
]
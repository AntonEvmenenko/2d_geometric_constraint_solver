from constraint import Constraint
from constraints import constraint_types
from point import Point
from segment import Segment
from arc import Arc

def example0(geometry, constraints):
    geometry.segments = [
        Segment(Point(300, 300), Point(500, 300)),
        Segment(Point(500, 300), Point(400, 200)),
        Segment(Point(400, 200), Point(300, 300)),
        
        Segment(Point(500, 300), Point(600, 250)),
        Segment(Point(600, 250), Point(400, 200)),
    ]

    constraints.clear()
    constraints += [
        Constraint([geometry.segments[0].p1, geometry.segments[2].p2], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], constraint_types.COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[3].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[3].p2, geometry.segments[4].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[4].p2, geometry.segments[1].p2], constraint_types.COINCIDENCE),

        Constraint([geometry.segments[1], geometry.segments[2]], constraint_types.EQUAL_LENGTH_OR_RADIUS),
        Constraint([geometry.segments[3], geometry.segments[4]], constraint_types.EQUAL_LENGTH_OR_RADIUS),
        Constraint([geometry.segments[3], geometry.segments[1]], constraint_types.EQUAL_LENGTH_OR_RADIUS),

        Constraint([geometry.segments[0].p1], constraint_types.FIXED),
        Constraint([geometry.segments[0].p2], constraint_types.FIXED),
    ]

def example1(geometry, constraints):
    geometry.segments = [
        Segment(Point(300, 200), Point(300, 400)),
        Segment(Point(300, 400), Point(500, 400)),
        Segment(Point(500, 400), Point(500, 200)),
    ]

    geometry.arcs = [
        Arc(Point(300, 200), Point(500, 200), Point(400, 100))
    ]

    constraints.clear()
    constraints += [
        Constraint([geometry.segments[0], geometry.arcs[0]], constraint_types.TANGENCY),
        Constraint([geometry.segments[2], geometry.arcs[0]], constraint_types.TANGENCY),

        Constraint([geometry.segments[0].p1, geometry.arcs[0].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[2].p2, geometry.arcs[0].p2], constraint_types.COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], constraint_types.COINCIDENCE),
    ]

def slot(geometry, constraints):
    geometry.segments = [
        Segment(Point(300, 200), Point(300, 400)),
        Segment(Point(500, 400), Point(500, 200)),
    ]

    geometry.arcs = [
        Arc(Point(300, 200), Point(500, 200), Point(400, 100)),
        Arc(Point(500, 400), Point(300, 400), Point(400, 500)),
    ]

    constraints.clear()
    constraints += [
        Constraint([geometry.segments[0], geometry.arcs[0]], constraint_types.TANGENCY),
        Constraint([geometry.segments[0], geometry.arcs[1]], constraint_types.TANGENCY),
        Constraint([geometry.segments[1], geometry.arcs[0]], constraint_types.TANGENCY),
        Constraint([geometry.segments[1], geometry.arcs[1]], constraint_types.TANGENCY),

        Constraint([geometry.segments[0].p1, geometry.arcs[0].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.arcs[1].p2], constraint_types.COINCIDENCE),

        Constraint([geometry.segments[1].p1, geometry.arcs[1].p1], constraint_types.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.arcs[0].p2], constraint_types.COINCIDENCE),
    ]

examples = [
    example0,
    example1,
    slot,
]
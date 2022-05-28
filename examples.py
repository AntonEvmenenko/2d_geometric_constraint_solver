from constraint import Constraint
from constraints import COINCIDENCE, EQUAL_LENGTH, FIXED
from point import Point
from segment import Segment

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
        Constraint([geometry.segments[0].p1, geometry.segments[2].p2], COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[3].p1], COINCIDENCE),
        Constraint([geometry.segments[3].p2, geometry.segments[4].p1], COINCIDENCE),
        Constraint([geometry.segments[4].p2, geometry.segments[1].p2], COINCIDENCE),

        Constraint([geometry.segments[1], geometry.segments[2]], EQUAL_LENGTH),
        Constraint([geometry.segments[3], geometry.segments[4]], EQUAL_LENGTH),
        Constraint([geometry.segments[3], geometry.segments[1]], EQUAL_LENGTH),

        Constraint([geometry.segments[0].p1], FIXED),
        Constraint([geometry.segments[0].p2], FIXED),
    ]
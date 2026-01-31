from constraints.constraint import Constraint
from constraints.constraints import CONSTRAINT_TYPE
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
        Constraint([geometry.segments[0].p1, geometry.segments[2].p2], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], CONSTRAINT_TYPE.COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[3].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[3].p2, geometry.segments[4].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[4].p2, geometry.segments[1].p2], CONSTRAINT_TYPE.COINCIDENCE),

        Constraint([geometry.segments[1], geometry.segments[2]], CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS),
        Constraint([geometry.segments[3], geometry.segments[4]], CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS),
        Constraint([geometry.segments[3], geometry.segments[1]], CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS),

        Constraint([geometry.segments[0].p1], CONSTRAINT_TYPE.FIXED),
        Constraint([geometry.segments[0].p2], CONSTRAINT_TYPE.FIXED),
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
        Constraint([geometry.segments[0], geometry.arcs[0]], CONSTRAINT_TYPE.TANGENCY),
        Constraint([geometry.segments[2], geometry.arcs[0]], CONSTRAINT_TYPE.TANGENCY),

        Constraint([geometry.segments[0].p1, geometry.arcs[0].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[2].p2, geometry.arcs[0].p2], CONSTRAINT_TYPE.COINCIDENCE),

        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], CONSTRAINT_TYPE.COINCIDENCE),
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
        Constraint([geometry.segments[0], geometry.arcs[0]], CONSTRAINT_TYPE.TANGENCY),
        Constraint([geometry.segments[0], geometry.arcs[1]], CONSTRAINT_TYPE.TANGENCY),
        Constraint([geometry.segments[1], geometry.arcs[0]], CONSTRAINT_TYPE.TANGENCY),
        Constraint([geometry.segments[1], geometry.arcs[1]], CONSTRAINT_TYPE.TANGENCY),

        Constraint([geometry.segments[0].p1, geometry.arcs[0].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[0].p2, geometry.arcs[1].p2], CONSTRAINT_TYPE.COINCIDENCE),

        Constraint([geometry.segments[1].p1, geometry.arcs[1].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.arcs[0].p2], CONSTRAINT_TYPE.COINCIDENCE),
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
        Constraint([geometry.segments[0].p2, geometry.segments[1].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[1].p2, geometry.segments[2].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[2].p2, geometry.segments[3].p1], CONSTRAINT_TYPE.COINCIDENCE),
        Constraint([geometry.segments[3].p2, geometry.segments[0].p1], CONSTRAINT_TYPE.COINCIDENCE),
    ]

def Chain(geometry, constraints):
    clear_geometry_and_constraints(geometry, constraints)

    x, y = 300, 300
    link_length = 100
    num_links = 15
    
    directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    current_dir_idx = 0
    
    current_side_length = 1
    links_placed_on_side = 0
    sides_completed = 0

    geometry.segments = []
    
    for i in range(num_links):
        dx_dir, dy_dir = directions[current_dir_idx]
        
        dx = dx_dir * link_length
        dy = dy_dir * link_length
        
        p1 = Point(x * SCALE, y * SCALE)
        p2 = Point((x + dx) * SCALE, (y + dy) * SCALE)
        geometry.segments.append(Segment(p1, p2))
        
        x += dx
        y += dy
        
        links_placed_on_side += 1
        
        if links_placed_on_side == current_side_length:
            current_dir_idx = (current_dir_idx + 1) % 4
            links_placed_on_side = 0
            sides_completed += 1
            if sides_completed == 2:
                current_side_length += 1
                sides_completed = 0

    constraints.append(Constraint([geometry.segments[0], link_length], CONSTRAINT_TYPE.LENGTH))
    constraints.append(Constraint([geometry.segments[0].p1], CONSTRAINT_TYPE.FIXED))

    for i in range(len(geometry.segments) - 1):
        prev_seg = geometry.segments[i]
        next_seg = geometry.segments[i+1]
        
        constraints.append(Constraint([prev_seg, next_seg], CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS))
        constraints.append(Constraint([prev_seg.p2, next_seg.p1], CONSTRAINT_TYPE.COINCIDENCE))

examples = [
    Lines,
    CutSlot,
    Slot,
    Rect,
    Chain,
]
from math import atan2, degrees, pi
from point import Point, distance_p2p
from line import Line, intersection_line_line
from vector import Vector, cross

ARC_DIRECTION_CW = 0
ARC_DIRECTION_CCW = 1

class Arc:
    # p1, p2 -- beginning and end of the arc
    # p -- random point that belongs to the arc
    def __init__(self, p1: Point, p2: Point, p: Point):
        self.p1 = p1
        self.p2 = p2

        p1_p = Vector.from_two_points(p1, p)
        p_p2 = Vector.from_two_points(p, p2)

        p1_p_segment_center = p1 + p1_p / 2
        p_p2_segment_center = p + p_p2 / 2

        l1 = Line(p1_p_segment_center, p1_p_segment_center + p1_p.rotated90ccw())
        l2 = Line(p_p2_segment_center, p_p2_segment_center + p_p2.rotated90ccw())

        self.center = intersection_line_line(l1, l2)

        assert self.center != None

        center_p1 = Vector.from_two_points(self.center, self.p1)
        center_p = Vector.from_two_points(self.center, p)

        self.direction = ARC_DIRECTION_CW if cross(center_p1, center_p) > 0 else ARC_DIRECTION_CCW

    def points(self):
        return [self.p1, self.p2, self.center]

    def radius(self):
        return Vector.from_two_points(self.p1, self.center).length()

    def bb_coords(self):
        radius = self.radius()
        return self.center.x - radius, self.center.y - radius, self.center.x + radius, self.center.y + radius, 
        
    def update_center(self):
        p1_p2 = Vector.from_two_points(self.p1, self.p2)
        p1_p2_segment_center = self.p1 + p1_p2 / 2

        l = Line(p1_p2_segment_center, p1_p2_segment_center + p1_p2.rotated90ccw())
        
        intersection = l.project_point_on_line(self.center)

        assert not intersection is None

        self.center.x, self.center.y = intersection.x, intersection.y

    def invert_direction(self):
        self.direction = ARC_DIRECTION_CW if self.direction == ARC_DIRECTION_CCW else ARC_DIRECTION_CCW

def distance_p2a(p: Point, arc: Arc):
    c_p1 = Vector.from_two_points(arc.center, arc.p1)
    c_p2 = Vector.from_two_points(arc.center, arc.p2)
    c_p = Vector.from_two_points(arc.center, p)

    def angle_to_0_2pi(angle):
        if angle < 0:
            return angle + 2 * pi
        if angle > 2 * pi:
            return angle - 2 * pi
        return angle

    # https://stackoverflow.com/questions/14066933/direct-way-of-computing-clockwise-angle-between-2-vectors
    def angle_cw(a, b):
        dot = a.x*b.x + a.y*b.y
        det = a.x*b.y - a.y*b.x
        return angle_to_0_2pi(atan2(det, dot))
    
    def equal(a, b):
        return abs(a - b) < 1e-5

    a = arc.direction == ARC_DIRECTION_CW and equal(angle_cw(c_p1, c_p) + angle_cw(c_p, c_p2), angle_cw(c_p1, c_p2))
    b = arc.direction == ARC_DIRECTION_CCW and equal(angle_cw(c_p2, c_p) + angle_cw(c_p, c_p1), angle_cw(c_p2, c_p1))
    is_inside_sector = a or b

    if is_inside_sector:
        return abs(arc.radius() - distance_p2p(arc.center, p))
    else:
        return min(distance_p2p(p, arc.p1), distance_p2p(p, arc.p2))

    

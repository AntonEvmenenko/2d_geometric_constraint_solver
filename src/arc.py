from enum import auto
from math import atan2, degrees, pi

from prometheus_client import Enum
from common import equal_eps, v2v_angle_cw
from point import Point, distance_p2p
from line import Line, intersection_line_line
from vector import Vector, cross, dot

class DIRECTION(Enum):
    CW      = auto()
    CCW     = auto()

class Arc:
    # p1, p2 -- beginning and end of the arc
    # p -- random point that belongs to the arc
    # direction is always CW (left-handed coordinate system)
    def __init__(self, p1: Point, p2: Point, p: Point):
        self.p1 = p1
        self.p2 = p2

        p1_p = Vector.from_two_points(p1, p)
        p_p2 = Vector.from_two_points(p, p2)
        p1_p2 = Vector.from_two_points(p1, p2)

        p1_p_segment_center = p1 + p1_p / 2
        p_p2_segment_center = p + p_p2 / 2
        p1_p2_segment_center = p1 + p1_p2 / 2

        l1 = Line(p1_p_segment_center, p1_p_segment_center + p1_p.rotated90ccw())
        l2 = Line(p_p2_segment_center, p_p2_segment_center + p_p2.rotated90ccw())

        center = intersection_line_line(l1, l2)

        assert center != None

        center_p1 = Vector.from_two_points(center, self.p1)
        center_p = Vector.from_two_points(center, p)

        dir = DIRECTION.CW if cross(center_p1, center_p) > 0 else DIRECTION.CCW

        if dir == DIRECTION.CCW:
            self.p1, self.p2 = self.p2, self.p1
            dir = DIRECTION.CW

        self.d = dot(Vector.from_two_points(p1_p2_segment_center, center), self.get_n())

    def get_n(self):
        return Vector.from_two_points(self.p1, self.p2).rotated90ccw().normalized()

    def center(self):
        p1_p2 = Vector.from_two_points(self.p1, self.p2)
        p1_p2_segment_center = self.p1 + p1_p2 / 2

        return p1_p2_segment_center + self.get_n() * self.d

    def points(self):
        return [self.p1, self.p2]

    def radius(self):
        return Vector.from_two_points(self.p1, self.center()).length()

    def bb_coords(self):
        radius = self.radius()
        center = self.center()
        return center.x - radius, center.y - radius, center.x + radius, center.y + radius

    def invert_direction(self):
        self.p1, self.p2 = self.p2, self.p1

    def middle_point(self):
        center = self.center()

        c_p1 = Vector.from_two_points(center, self.p1)
        c_p2 = Vector.from_two_points(center, self.p2)

        angle = v2v_angle_cw(c_p1, c_p2)

        return center + c_p1.rotated(angle / 2)


def distance_p2a(p: Point, arc: Arc):
    arc_center = arc.center()

    c_p1 = Vector.from_two_points(arc_center, arc.p1)
    c_p2 = Vector.from_two_points(arc_center, arc.p2)
    c_p = Vector.from_two_points(arc_center, p)

    is_inside_sector = equal_eps(v2v_angle_cw(c_p1, c_p) + v2v_angle_cw(c_p, c_p2), v2v_angle_cw(c_p1, c_p2))

    if is_inside_sector:
        return abs(arc.radius() - distance_p2p(arc_center, p))
    else:
        return min(distance_p2p(p, arc.p1), distance_p2p(p, arc.p2))

    

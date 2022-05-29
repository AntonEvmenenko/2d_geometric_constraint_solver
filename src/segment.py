from point import Point, distance_p2p
from vector import Vector, cross, dot

class Segment:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def vector(self):
        return Vector.from_two_points(self.p1, self.p2)

    def points(self):
        return [self.p1, self.p2]

    def __contains__(self, p: Point):
        between = lambda a, b, x: (a <= x <= b) or (b <= x <= a)

        p1_p = Vector.from_two_points(self.p1, p)

        a = cross(p1_p, self.vector()) / self.vector().length()
        b = between(self.p1.x, self.p2.x, p.x) and between(self.p1.y, self.p2.y, p.y)

        return abs(a) < 1e-5 and b

def distance_p2s(p: Point, s: Segment):
    p1_p2 = s.vector()
    p1_p = Vector.from_two_points(s.p1, p)

    point_to_line_distance = abs(cross(p1_p, p1_p2) / p1_p2.length())

    p1_p2_unit = p1_p2.normalized()

    projection_length = dot(p1_p, p1_p2_unit)
    projection_point = s.p1 + p1_p2_unit * projection_length

    if projection_point in s:
        return point_to_line_distance
    else:
        return min(distance_p2p(p, s.p1), distance_p2p(p, s.p2))
from geometric_primitives.point import Point
from geometric_primitives.vector import Vector

# def line(p1, p2):
#     A = (p1[1] - p2[1])
#     B = (p2[0] - p1[0])
#     C = (p1[0]*p2[1] - p2[0]*p1[1])
#     return A, B, -C

class Line:
    def __init__(self, p1: Point, p2: Point):
        self.a = p1.y - p2.y
        self.b = p2.x - p1.x
        self.c = p1.y * p2.x - p1.x * p2.y

    def get_normal(self):
        return Vector(self.a, self.b)

    def project_point_on_line(self, p: Point):
        l = Line(p, p + self.get_normal())
        intersection = intersection_line_line(self, l)
        assert not intersection is None
        return intersection

def intersection_line_line(l1, l2):
    d  = l1.a * l2.b - l1.b * l2.a
    dx = l1.c * l2.b - l1.b * l2.c
    dy = l1.a * l2.c - l1.c * l2.a

    if abs(d) < 1e-5:
        return None

    return Point(dx / d, dy / d)

def distance_p2l(p: Point, l: Line):
    projection = l.project_point_on_line(p)
    return Vector.from_two_points(p, projection).length()
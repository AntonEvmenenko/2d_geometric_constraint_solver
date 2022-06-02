from math import cos, sin, sqrt

def dot(v1, v2):
    return v1.x * v2.x + v1.y * v2.y

def cross(v1, v2):
    return v1.x * v2.y - v1.y * v2.x

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_two_points(cls, p1, p2):
        return cls(p2.x - p1.x, p2.y - p1.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        return Vector(self.x * k, self.y * k)

    def __truediv__(self, k):
        return Vector(self.x / k, self.y / k)

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        return self / self.length()

    def rotated(self, angle):
        return Vector(cos(angle) * self.x - sin(angle) * self.y, sin(angle) * self.x + cos(angle) * self.y)

    # for left-handed coordinate system
    def rotated90ccw(self):
        return Vector(self.y, -self.x)

    # for left-handed coordinate system
    def rotated90cw(self):
        return Vector(-self.y, self.x)
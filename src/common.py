from math import atan2, pi
from vector import cross, dot

def angle_to_0_2pi(angle):
    if angle < 0:
        return angle + 2 * pi
    if angle > 2 * pi:
        return angle - 2 * pi
    return angle

# https://stackoverflow.com/questions/14066933/direct-way-of-computing-clockwise-angle-between-2-vectors
def v2v_angle_cw(a, b):
    return angle_to_0_2pi(atan2(cross(a, b), dot(a, b)))

def equal_eps(a, b, eps = 1e-5):
    return abs(a - b) < eps

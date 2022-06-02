from geometric_primitives.arc import Arc
from geometric_primitives.point import Point
from geometric_primitives.segment import Segment

class Geometry:
    def __init__(self):
        self.segments = []
        self.arcs = []
        # self.circles = []

    def clear(self):
        self.segments = []
        self.arcs = []

    def remove_entity(self, entity):
        if isinstance(entity, Segment):
            self.segments.remove(entity)
        elif isinstance(entity, Arc):
            self.arcs.remove(entity)
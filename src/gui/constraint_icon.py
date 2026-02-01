from geometric_primitives.point import Point
import tkinter as tk

class ConstraintIcon():
    def __init__(self, canvas, icon, icon_size):
        self.canvas = canvas
        self.icon = icon
        self.icon_width = icon_size
        self.icon_height = icon_size
        self.point = Point(0, 0)
        self.add_drawn_entities()

    def add_drawn_entities(self):
        center_point = Point(0, 0)
        
        self.icon = self.canvas.create_image((center_point.x, center_point.y), image = self.icon)
        
        self.background = self.create_rounded_rectangle(center_point.x - self.icon_width / 2, center_point.y - self.icon_height / 2, \
            center_point.x + self.icon_width / 2, center_point.y + self.icon_height / 2, fill="pale green")
        self.canvas.tag_lower(self.background)

    def remove_drawn_entities(self):
        self.canvas.delete(self.background)
        self.canvas.delete(self.icon)

    def moveto(self, point):
        self.point = point
        self.canvas.moveto(self.background, int(point.x - self.icon_width // 2 - 1), int(point.y - self.icon_height // 2 - 1))
        self.canvas.moveto(self.icon, int(point.x - self.icon_width // 2), int(point.y - self.icon_height // 2))

    def set_selected(self, selected):
        color = "red" if selected else "pale green"
        self.canvas.itemconfig(self.background, fill = color)

    def create_rounded_rectangle(self, x1, y1, x2, y2, r = 10, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, \
            x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def __contains__(self, p):
        return (self.point.x - self.icon_width / 2 <= p.x <= self.point.x + self.icon_width / 2) and (self.point.y - self.icon_height / 2 <= p.y <= self.point.y + self.icon_height / 2)
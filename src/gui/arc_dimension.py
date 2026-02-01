from geometric_primitives.arc import Arc
from geometric_primitives.vector import Vector
import tkinter as tk
import math
from gui.config import *

class ArcDimension():
    def __init__(self, canvas, value):
        self.canvas = canvas
        self.value = value
        self.add_drawn_entities()

    def add_drawn_entities(self):
        self.dimension_line = self.canvas.create_line(0, 0, 0, 0, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=EXTENSION_LINE_THICKNESS, arrow=tk.LAST)
        self.value_icon = self.canvas.create_text((0, 0), font = "TkDefaultFont", text = self.value)

    def remove_drawn_entities(self):
        self.canvas.delete(self.dimension_line)
        self.canvas.delete(self.value_icon)

    def moveto(self, arc):
        self.arc = arc

        dl_p1_x = arc.center().x
        dl_p1_y = arc.center().y
        dl_p2_x = arc.middle_point().x
        dl_p2_y = arc.middle_point().y

        self.canvas.coords(self.dimension_line, dl_p1_x, dl_p1_y, dl_p2_x, dl_p2_y)

        n = Vector(dl_p2_x - dl_p1_x, dl_p2_y - dl_p1_y).normalized().rotated90cw()
        
        text_x = (dl_p1_x + dl_p2_x) / 2 + n.x * 10
        text_y = (dl_p1_y + dl_p2_y) / 2 + n.y * 10
        
        dx = dl_p2_x - dl_p1_x
        dy = dl_p2_y - dl_p1_y
        angle = math.degrees(math.atan2(dy, dx)) 
        
        if angle > 90 or angle < -90:
            angle += 180

        self.canvas.coords(self.value_icon, text_x, text_y)
        self.canvas.itemconfigure(self.value_icon, angle=-angle)

    def set_selected(self, selected):
        color = "red" if selected else "black"
        self.canvas.itemconfig(self.dimension_line, fill = color)
        self.canvas.itemconfig(self.value_icon, fill = color)

    def __contains__(self, p):
        tolerance = 3 
        
        items_nearby = self.canvas.find_overlapping(
            p.x - tolerance, p.y - tolerance, 
            p.x + tolerance, p.y + tolerance
        )
        
        my_entities = {
            self.dimension_line, 
            self.value_icon
        }
        
        for item_id in items_nearby:
            if item_id in my_entities:
                return True
                
        return False
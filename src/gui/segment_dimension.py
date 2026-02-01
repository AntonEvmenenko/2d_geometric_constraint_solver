from geometric_primitives.segment import Segment
import tkinter as tk
import math
from gui.config import *

class SegmentDimension():
    def __init__(self, canvas, value):
        self.canvas = canvas
        self.value = value
        self.add_drawn_entities()

    def add_drawn_entities(self):
        self.left_extension_line = self.canvas.create_line(0, 0, 0, 0, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=EXTENSION_LINE_THICKNESS)
        self.right_extension_line = self.canvas.create_line(0, 0, 0, 0, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=EXTENSION_LINE_THICKNESS)
        self.dimension_line = self.canvas.create_line(0, 0, 0, 0, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=EXTENSION_LINE_THICKNESS, arrow=tk.BOTH)
        self.value_icon = self.canvas.create_text((0, 0), font = "TkDefaultFont", text = self.value)
        self.canvas.tag_lower(self.left_extension_line)
        self.canvas.tag_lower(self.right_extension_line)

    def remove_drawn_entities(self):
        self.canvas.delete(self.left_extension_line)
        self.canvas.delete(self.right_extension_line)
        self.canvas.delete(self.dimension_line)
        self.canvas.delete(self.value_icon)

    def moveto(self, segment):
        self.segment = segment

        n = self.segment.vector().normalized().rotated90cw()

        self.canvas.coords(self.left_extension_line, self.segment.p1.x, self.segment.p1.y, self.segment.p1.x + n.x * EXTENSION_LINE_LENGTH, self.segment.p1.y + n.y * EXTENSION_LINE_LENGTH)
        self.canvas.coords(self.right_extension_line, self.segment.p2.x, self.segment.p2.y, self.segment.p2.x + n.x * EXTENSION_LINE_LENGTH, self.segment.p2.y + n.y * EXTENSION_LINE_LENGTH)
        
        dl_p1_x = self.segment.p1.x + n.x * DIMENSION_LINE_OFFSET
        dl_p1_y = self.segment.p1.y + n.y * DIMENSION_LINE_OFFSET
        dl_p2_x = self.segment.p2.x + n.x * DIMENSION_LINE_OFFSET
        dl_p2_y = self.segment.p2.y + n.y * DIMENSION_LINE_OFFSET
        
        self.canvas.coords(self.dimension_line, dl_p1_x, dl_p1_y, dl_p2_x, dl_p2_y)

        text_x = (dl_p1_x + dl_p2_x) / 2 + n.x * 10
        text_y = (dl_p1_y + dl_p2_y) / 2 + n.y * 10
        
        dx = self.segment.p2.x - self.segment.p1.x
        dy = self.segment.p2.y - self.segment.p1.y
        angle = math.degrees(math.atan2(dy, dx)) 
        
        if angle > 90 or angle < -90:
            angle += 180

        self.canvas.coords(self.value_icon, text_x, text_y)
        self.canvas.itemconfigure(self.value_icon, angle=-angle)

    def set_selected(self, selected):
        color = "red" if selected else "black"
        self.canvas.itemconfig(self.left_extension_line, fill = color)
        self.canvas.itemconfig(self.right_extension_line, fill = color)
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
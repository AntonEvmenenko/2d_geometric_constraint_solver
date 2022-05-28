import tkinter as tk
from constraint import Constraint
from constraints import *
from examples import example0

from geometry import Geometry
from point import Point, distance_p2p
from segment import Segment, distance_p2s

USER_SELECTING_RADUIS = 10
POINT_RADIUS = 4

class GUI(tk.Frame):
    def __init__(self, root, geometry: Geometry, geometry_changed_callback, constraints, constraints_changed_callback):
        tk.Frame.__init__(self, root)

        self.root = root

        self.geometry = geometry
        self.geometry_changed_callback = geometry_changed_callback

        self.constraints = constraints
        self.constraints_changed_callback = constraints_changed_callback

        self.canvas = tk.Canvas(self, width=800, height=600, background='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.segment_to_drawn_line = {}
        self.point_to_drawn_circle = {}

        self.selected_point = None
        self.selected_point_moved = False

        self.points_for_new_geometry = []
        self.adding_segment = False
        self.adding_arc = False
        self.adding_circle = False

        self.selected_points = []
        self.selected_segments = []

        self.create_text_hint()
        self.create_side_menus()
        self.create_top_menu()
        self.create_bindings()
        self.create_buttons()
        self.add_geometry()

    def create_text_hint(self):
        self.text_hint = tk.Label(self, bd=0, background='white')

    def set_text_hint(self, text):
        self.text_hint.config(text = text)

    def create_top_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff="off")
        file_menu.add_command(label='0', command=lambda: self.load_example(example0))
        menubar.add_cascade(label="Examples", menu=file_menu)

    def create_side_menus(self):
        self.menu_left = tk.Frame(self)
        self.menu_right = tk.Frame(self)

    def create_bindings(self):
        # left mouse button bindings
        self.canvas.bind("<ButtonPress-1>", self.on_left_button_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_button_released)
        self.canvas.bind("<B1-Motion>", self.on_left_button_moved)

        # middle button bindings (panning)
        self.canvas.bind("<ButtonPress-2>", self.on_middle_mouse_button_pressed)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_mouse_button_released)
        self.canvas.bind("<B2-Motion>", self.on_middle_mouse_button_move)

        # wheel bindings (zoom)

        # linux scroll
        # TODO: check if we really need it
        # self.canvas.bind("<Button-4>", self.on_zoom_in)
        # self.canvas.bind("<Button-5>", self.on_zoom_out)

        # windows zoom
        # self.canvas.bind("<MouseWheel>",self.on_zoom)
        
        # resize of the main window
        self.bind("<Configure>", self.on_resize)

    def create_buttons(self):
        self.line_icon = tk.PhotoImage(file = "icons/line_icon.png")
        self.arc_icon = tk.PhotoImage(file = "icons/arc_icon.png")
        self.circle_icon = tk.PhotoImage(file = "icons/circle_icon.png")
        tk.Button(self.menu_left, image = self.line_icon, bg = "white", command = self.on_add_segment_button_clicked).grid(row = 0, column = 1, sticky="n")
        tk.Button(self.menu_left, image = self.arc_icon, bg = "white", state=tk.DISABLED).grid(row = 1, column = 1, sticky="n")
        tk.Button(self.menu_left, image = self.circle_icon, bg = "white", state=tk.DISABLED).grid(row = 2, column = 1, sticky="n")

        tk.Button(self.menu_right, text = 'COI', width = 4, command = self.on_add_coincidence_constraint_button_clicked).grid(row = 0, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'PER', width = 4, command = self.on_add_perpendicular_constraint_button_clicked).grid(row = 1, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'PAR', width = 4, command = self.on_add_parallel_constraint_button_clicked).grid(row = 2, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'TAN', width = 4, state=tk.DISABLED).grid(row = 3, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'FIX', width = 4, command = self.on_add_fixed_constraint_button_clicked).grid(row = 4, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'DIM', width = 4, state=tk.DISABLED).grid(row = 5, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'EQL', width = 4, command = self.on_add_equal_length_constraint_button_clicked).grid(row = 6, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'HOR', width = 4, command = self.on_add_horizontality_constraint_button_clicked).grid(row = 7, column = 1, sticky="n")
        tk.Button(self.menu_right, text = 'VER', width = 4, command = self.on_add_verticality_constraint_button_clicked).grid(row = 8, column = 1, sticky="n")

        # tk.Button(self.menu_right, text = 'RBL', width = 4, command = self.on_rebuild_button_clicked).grid(row = 7, column = 1, sticky="s")

    def load_example(self, example):
        example(self.geometry, self.constraints)
        self.add_geometry()
        self.constraints_changed_callback()

    def add_geometry(self):
        for segment in self.geometry.segments:
            self.add_segment(segment)

    def add_segment(self, segment):
        line = self.canvas.create_line(segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=2)
        self.segment_to_drawn_line[segment] = line

        self.point_to_drawn_circle[segment.p1] = self.canvas.create_oval(segment.p1.x - POINT_RADIUS, segment.p1.y - POINT_RADIUS, segment.p1.x + POINT_RADIUS, segment.p1.y + POINT_RADIUS, fill='blue', outline='blue')
        self.point_to_drawn_circle[segment.p2] = self.canvas.create_oval(segment.p2.x - POINT_RADIUS, segment.p2.y - POINT_RADIUS, segment.p2.x + POINT_RADIUS, segment.p2.y + POINT_RADIUS, fill='blue', outline='blue')

    def redraw_geometry(self):
        for segment in self.geometry.segments:
            # TODO: check if we really need to update coords

            self.canvas.coords(self.segment_to_drawn_line[segment], segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y)

            self.canvas.coords(self.point_to_drawn_circle[segment.p1], segment.p1.x - POINT_RADIUS, segment.p1.y - POINT_RADIUS, segment.p1.x + POINT_RADIUS, segment.p1.y + POINT_RADIUS)
            self.canvas.coords(self.point_to_drawn_circle[segment.p2], segment.p2.x - POINT_RADIUS, segment.p2.y - POINT_RADIUS, segment.p2.x + POINT_RADIUS, segment.p2.y + POINT_RADIUS)

            line_color = "red" if segment in self.selected_segments else "black"
            self.canvas.itemconfig(self.segment_to_drawn_line[segment], fill=line_color)

            self.canvas.itemconfig(self.point_to_drawn_circle[segment.p1], fill='blue', outline='blue')
            self.canvas.itemconfig(self.point_to_drawn_circle[segment.p2], fill='blue', outline='blue')

        for selected_point in self.selected_points:
            circle = self.point_to_drawn_circle[selected_point]
            self.canvas.itemconfig(circle, fill='red', outline='red')
            self.canvas.tag_raise(circle)


    def on_left_button_pressed(self, event):
        cursor = Point(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        
        if self.adding_segment:
            self.points_for_new_geometry.append(cursor)

            self.set_text_hint(f'Select point {len(self.points_for_new_geometry) + 1}')

            if len(self.points_for_new_geometry) == 2:
                segment = Segment(self.points_for_new_geometry[0], self.points_for_new_geometry[1])
                self.geometry.segments.append(segment)
                self.add_segment(segment)
                self.new_geometry_added()
                return

            return

        for segment in self.geometry.segments:
            for point in segment.points():
                if distance_p2p(point, cursor) < USER_SELECTING_RADUIS:
                    self.selected_point = point
                    self.selected_points.append(point)
                    self.redraw_geometry()
                    return
            # if segment.has_point(cursor):
            if distance_p2s(cursor, segment) < USER_SELECTING_RADUIS:
                self.selected_segments.append(segment)
                self.redraw_geometry()
                return

        self.selected_segments.clear()
        self.selected_points.clear()
        self.redraw_geometry()

    def on_left_button_released(self, event):
        if self.selected_point_moved:
            self.selected_points.remove(self.selected_point)
            self.redraw_geometry()
        self.selected_point = None
        self.selected_point_moved = False

    def on_left_button_moved(self, event):
        if self.selected_point is None:
            return

        for constraint in self.constraints:
            if (constraint.type == FIXED) and (self.selected_point in constraint.entities):
                return

        self.selected_point_moved = True

        cursor = Point(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        self.selected_point.x, self.selected_point.y = cursor.x, cursor.y

        self.geometry_changed_callback(self.selected_point)

    def on_middle_mouse_button_pressed(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_middle_mouse_button_released(self, event):    
        pass
    
    def on_middle_mouse_button_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_resize(self, event):
        # TODO: refactor
        self.canvas.config(width=event.width - 4, height=event.height - 4)
        
        self.menu_left.place(x = 10, y = 10)
        self.menu_right.place(x = event.width - 45, y = 10)

        self.text_hint.place(x = 10, y = event.height - 25)

    # def on_zoom(self,event):
    #     factor = 1.1 if (event.delta > 0) else 0.9
    #     x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
    #     self.canvas.scale("all", x, y, factor, factor)

    # def on_zoom_in(self,event):
    #     self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        
    # def on_zoom_out(self,event):
    #     self.canvas.scale("all", event.x, event.y, 0.9, 0.9)

    def new_geometry_added(self):
        self.points_for_new_geometry.clear()

        self.adding_segment = False
        self.adding_arc = False
        self.adding_circle = False
        
        self.set_text_hint("")

        self.geometry_changed_callback(None)

    def on_add_segment_button_clicked(self):
        self.set_text_hint('Select point 1')
        self.adding_segment = True

    def on_add_perpendicular_constraint_button_clicked(self):
        self.constraints.append(Constraint([self.selected_segments[0], self.selected_segments[1]], PERPENDICULAR))

        self.selected_segments.clear()
        self.constraints_changed_callback()

    def on_add_parallel_constraint_button_clicked(self):
        self.constraints.append(Constraint([self.selected_segments[0], self.selected_segments[1]], PARALLEL))

        self.selected_segments.clear()
        self.constraints_changed_callback()

    def on_add_equal_length_constraint_button_clicked(self):
        self.constraints.append(Constraint([self.selected_segments[0], self.selected_segments[1]], EQUAL_LENGTH))

        self.selected_segments.clear()
        self.constraints_changed_callback()

    def on_add_horizontality_constraint_button_clicked(self):
        self.constraints.append(Constraint([self.selected_segments[0]], HORIZONTALITY))

        self.selected_segments.clear()
        self.constraints_changed_callback()

    def on_add_verticality_constraint_button_clicked(self):
        self.constraints.append(Constraint([self.selected_segments[0]], VERTICALITY))

        self.selected_segments.clear()
        self.constraints_changed_callback()

    def on_add_coincidence_constraint_button_clicked(self):
        print (f'coincidence cnstraint: {[self.selected_points[0], self.selected_points[1]]}')
        self.constraints.append(Constraint([self.selected_points[0], self.selected_points[1]], COINCIDENCE))
        
        self.selected_points.clear()
        self.constraints_changed_callback()

    def on_add_fixed_constraint_button_clicked(self):
        self.constraints.append(Constraint([self.selected_points[0]], FIXED))
        
        self.selected_points.clear()

    def on_rebuild_button_clicked(self):
        self.geometry_changed_callback(None, None)
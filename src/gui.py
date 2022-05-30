from copy import copy
import tkinter as tk
from tkinter.font import NORMAL
from constraint import Constraint
from constraints import *
from examples import examples
from geometry import Geometry
from point import Point, distance_p2p
from segment import Segment, distance_p2s
from math import atan2, degrees, pi
from arc import ARC_DIRECTION_CCW, ARC_DIRECTION_CW, Arc, distance_p2a

USER_SELECTING_RADUIS = 5
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
        
        # self.segment_to_drawn_line = {}
        # self.arc_to_drawn_arc = {}

        self.entity_to_drawn_entity = {}

        self.point_to_drawn_circle = {}
        self.entity_and_constraint_to_drawn_constraint_icon = {}

        self.selected_point = None
        self.selected_point_moved = False

        self.points_for_new_geometry = []
        self.adding_segment = False
        self.adding_arc = False

        self.selected_entities = set()

        self.create_text_hint()
        self.create_side_menus()
        self.create_top_menu()
        self.create_bindings()
        self.create_icons()
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
        for i, example in enumerate(examples):
            file_menu.add_command(label=f'{i}', command=lambda example = example: self.load_example(example))
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

    def create_icons(self):
        self.segment_icon =             tk.PhotoImage(file = "icons/32x32/segment.png")
        self.arc_icon =                 tk.PhotoImage(file = "icons/32x32/arc.png")
        self.circle_icon =              tk.PhotoImage(file = "icons/32x32/circle.png")

        self.constraint_icon_32x32 = {
            COINCIDENCE:        tk.PhotoImage(file = "icons/32x32/coincidence.png"),
            PARALLELITY:        tk.PhotoImage(file = "icons/32x32/parallelity.png"),
            PERPENDICULARITY:   tk.PhotoImage(file = "icons/32x32/perpendicularity.png"),
            EQUAL_LENGTH:       tk.PhotoImage(file = "icons/32x32/equal_length.png"),
            LENGTH:             tk.PhotoImage(file = "icons/32x32/length.png"),
            FIXED:              tk.PhotoImage(file = "icons/32x32/fixed.png"),
            HORIZONTALITY:      tk.PhotoImage(file = "icons/32x32/horizontality.png"),
            VERTICALITY:        tk.PhotoImage(file = "icons/32x32/verticality.png"),
            TANGENCY:           tk.PhotoImage(file = "icons/32x32/tangency.png"),
            CONCENTRICITY:      tk.PhotoImage(file = "icons/32x32/concentricity.png"),
        }

        self.constraint_icon_20x20 = {
            COINCIDENCE:        tk.PhotoImage(file = "icons/20x20/coincidence.png"),
            PARALLELITY:        tk.PhotoImage(file = "icons/20x20/parallelity.png"),
            PERPENDICULARITY:   tk.PhotoImage(file = "icons/20x20/perpendicularity.png"),
            EQUAL_LENGTH:       tk.PhotoImage(file = "icons/20x20/equal_length.png"),
            LENGTH:             tk.PhotoImage(file = "icons/20x20/length.png"),
            FIXED:              tk.PhotoImage(file = "icons/20x20/fixed.png"),
            HORIZONTALITY:      tk.PhotoImage(file = "icons/20x20/horizontality.png"),
            VERTICALITY:        tk.PhotoImage(file = "icons/20x20/verticality.png"),
            TANGENCY:           tk.PhotoImage(file = "icons/20x20/tangency.png"),
            CONCENTRICITY:      tk.PhotoImage(file = "icons/20x20/concentricity.png"),
        }

    def create_buttons(self):
        def create_menu_left_button(row, icon, command):
            tk.Button(self.menu_left, image = icon, command = command, relief = tk.SOLID, bg = "light gray", activebackground = "light gray").grid(row = row, column = 1, sticky = "n", pady = 2)

        create_menu_left_button(0, self.segment_icon, self.on_add_segment_button_clicked)
        create_menu_left_button(1, self.arc_icon, self.on_add_arc_button_clicked)
        # create_menu_left_button(2, self.circle_icon, None)

        def create_menu_right_constraint_button(row, constraint_type):
            button = tk.Button(self.menu_right, image = self.constraint_icon_32x32[constraint_type], \
                command = lambda: self.on_add_constraint_button_clicked(constraint_type), state=tk.DISABLED, relief = tk.SOLID, bg = "light gray", activebackground = "light gray")
            button.grid(row = row, column = 1, sticky="n", pady = 2)
            return button

        self.constraint_button = {
            COINCIDENCE:        create_menu_right_constraint_button(0, COINCIDENCE),
            FIXED:              create_menu_right_constraint_button(1, FIXED),
            PERPENDICULARITY:   create_menu_right_constraint_button(2, PERPENDICULARITY),
            PARALLELITY:        create_menu_right_constraint_button(3, PARALLELITY),
            EQUAL_LENGTH:       create_menu_right_constraint_button(4, EQUAL_LENGTH),
            VERTICALITY:        create_menu_right_constraint_button(5, VERTICALITY),
            HORIZONTALITY:      create_menu_right_constraint_button(6, HORIZONTALITY),
            TANGENCY:           create_menu_right_constraint_button(7, TANGENCY),
        }

    def load_example(self, example):
        example(self.geometry, self.constraints)
        self.add_geometry()
        self.constraints_changed_callback()

    def add_geometry(self):
        for segment in self.geometry.segments:
            self.add_segment(segment)

        for arc in self.geometry.arcs:
            self.add_arc(arc)

    def add_segment(self, segment: Segment):
        line = self.canvas.create_line(segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=2)
        self.canvas.tag_lower(line)
        self.entity_to_drawn_entity[segment] = line

        def create_point(point):
            return self.canvas.create_oval(point.x - POINT_RADIUS, point.y - POINT_RADIUS, point.x + POINT_RADIUS, point.y + POINT_RADIUS, fill='blue', outline='blue')

        self.point_to_drawn_circle[segment.p1] = create_point(segment.p1)
        self.point_to_drawn_circle[segment.p2] = create_point(segment.p2)

    def calculate_arc_start_and_extent(self, arc: Arc):
        center_p2 = Vector.from_two_points(arc.center, arc.p2)
        center_p1 = Vector.from_two_points(arc.center, arc.p1)

        start_angle = degrees(atan2(-center_p1.y, center_p1.x))
        end_angle = degrees(atan2(-center_p2.y, center_p2.x))

        if arc.direction == ARC_DIRECTION_CW and (end_angle > start_angle):
            start_angle += 360
        elif arc.direction == ARC_DIRECTION_CCW and (start_angle > end_angle):
            end_angle += 360

        extent = end_angle - start_angle

        # print (f"start, end, extent: {int(start_angle), int(end_angle), int(extent)}")

        return start_angle, extent

    def add_arc(self, arc: Arc):
        bb_coords = arc.bb_coords()

        start, extent = self.calculate_arc_start_and_extent(arc)
        # print (start, extent)

        drawn_arc = self.canvas.create_arc(bb_coords, start = start, extent = extent, style=tk.ARC, width=3)
        self.canvas.tag_lower(drawn_arc)
        self.entity_to_drawn_entity[arc] = drawn_arc 

        def create_point(point):
            return self.canvas.create_oval(point.x - POINT_RADIUS, point.y - POINT_RADIUS, point.x + POINT_RADIUS, point.y + POINT_RADIUS, fill='blue', outline='blue')

        self.point_to_drawn_circle[arc.p1] = create_point(arc.p1)
        self.point_to_drawn_circle[arc.p2] = create_point(arc.p2)
        self.point_to_drawn_circle[arc.center] = create_point(arc.center)

        # bb = self.canvas.create_rectangle(bb_coords)

    def redraw_geometry(self):
        # segments and arcs
        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                self.canvas.coords(self.point_to_drawn_circle[point], point.x - POINT_RADIUS, point.y - POINT_RADIUS, point.x + POINT_RADIUS, point.y + POINT_RADIUS)
                self.canvas.itemconfig(self.point_to_drawn_circle[point], fill='blue', outline='blue')

            line_color = "red" if entity in self.selected_entities else "black"
            self.canvas.itemconfig(self.entity_to_drawn_entity[entity], fill=line_color)
            if isinstance(entity, Arc):
                self.canvas.itemconfig(self.entity_to_drawn_entity[entity], outline=line_color)

        # segments
        for segment in self.geometry.segments:
            self.canvas.coords(self.entity_to_drawn_entity[segment], segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y)

        # arcs
        for arc in self.geometry.arcs:
            self.canvas.coords(self.entity_to_drawn_entity[arc], arc.bb_coords())
            start, extent = self.calculate_arc_start_and_extent(arc)
            self.canvas.itemconfig(self.entity_to_drawn_entity[arc], start = start, extent = extent)

        # selected points
        for selected_point in [entity for entity in self.selected_entities if isinstance(entity, Point)]:
            circle = self.point_to_drawn_circle[selected_point]
            self.canvas.itemconfig(circle, fill='red', outline='red')
            self.canvas.tag_raise(circle)

        self.update_constraint_icons()

    def on_left_button_pressed(self, event):
        cursor = Point(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        
        if self.adding_segment or self.adding_arc:
            self.points_for_new_geometry.append(cursor)

            self.set_text_hint(f'Select point {len(self.points_for_new_geometry) + 1}')

            if self.adding_segment and len(self.points_for_new_geometry) == 2:
                segment = Segment(self.points_for_new_geometry[0], self.points_for_new_geometry[1])
                self.geometry.segments.append(segment)
                self.add_segment(segment)
                self.new_geometry_added()
                return

            if self.adding_arc and len(self.points_for_new_geometry) == 3:
                arc = Arc(self.points_for_new_geometry[0], self.points_for_new_geometry[2], self.points_for_new_geometry[1])
                self.geometry.arcs.append(arc)
                self.add_arc(arc)
                self.new_geometry_added()
                return
            return

        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                if distance_p2p(point, cursor) < USER_SELECTING_RADUIS:
                    self.selected_point = point
                    self.selected_entities.add(point)
                    self.check_constraints_requirements()
                    self.redraw_geometry()
                    return
            if isinstance(entity, Segment) and distance_p2s(cursor, entity) < USER_SELECTING_RADUIS:
                self.selected_entities.add(entity)
                self.check_constraints_requirements()
                self.redraw_geometry()
                return

            if isinstance(entity, Arc) and distance_p2a(cursor, entity) < USER_SELECTING_RADUIS:
                if entity in self.selected_entities: # "double click"
                    entity.invert_direction()
                self.selected_entities.add(entity)
                self.check_constraints_requirements()
                self.redraw_geometry()
                return

        self.selected_entities.clear()
        self.check_constraints_requirements()
        self.redraw_geometry()

    def on_left_button_released(self, event):
        if self.selected_point_moved:
            self.selected_entities.remove(self.selected_point)
            self.check_constraints_requirements()
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
        
        self.set_text_hint("")

        self.geometry_changed_callback(None)

    def on_add_segment_button_clicked(self):
        self.set_text_hint('Select point 1')
        self.adding_segment = True

    def on_add_arc_button_clicked(self):
        self.set_text_hint('Select point 1')
        self.adding_arc = True

    def on_add_constraint_button_clicked(self, constraint_type):
        self.constraints.append(Constraint(list(self.selected_entities), constraint_type))

        self.selected_entities.clear()
        self.constraints_changed_callback()

    def check_constraints_requirements(self):
        for button in self.constraint_button.values():
            button.configure(state = tk.DISABLED)

        for constraint_type in get_available_constraints(self.selected_entities):
            self.constraint_button[constraint_type].configure(state = tk.NORMAL)

    def update_constraint_icons(self):
        # constraint icons for segments
        for segment in self.geometry.segments:
            drawn_icons = []

            for constraint in self.constraints:
                if segment in constraint.entities:
                    if not (segment, constraint) in self.entity_and_constraint_to_drawn_constraint_icon:
                        self.entity_and_constraint_to_drawn_constraint_icon[(segment, constraint)] = ConstraintIcon(self.canvas, self.constraint_icon_20x20[constraint.type], 20)
                    drawn_icons.append(self.entity_and_constraint_to_drawn_constraint_icon[(segment, constraint)])

            normal_spacing = 20
            tangent_spacing = 30

            tangent_offset = max(tangent_spacing * (len(drawn_icons) - 1), 0) / 2

            p1_p2 = Vector.from_two_points(segment.p1, segment.p2)
            p1_p2_unit = p1_p2.normalized()
            center_point = segment.p1 + p1_p2 / 2
            n = Vector(p1_p2_unit.y, -p1_p2_unit.x)

            for i, drawn_icon in enumerate(drawn_icons):
                drawn_icon.moveto(center_point + n * normal_spacing + p1_p2_unit * (-tangent_offset) + p1_p2_unit * (i * tangent_spacing))

        # constraint icons for points
        for segment in self.geometry.segments:
            for point in segment.points():
                drawn_icons = []

                for constraint in self.constraints:
                    if point in constraint.entities:
                        if not (point, constraint) in self.entity_and_constraint_to_drawn_constraint_icon:

                            exists_already = (constraint.type == COINCIDENCE) and any(c is constraint for (p, c) in self.entity_and_constraint_to_drawn_constraint_icon)

                            if not exists_already:
                                self.entity_and_constraint_to_drawn_constraint_icon[(point, constraint)] = ConstraintIcon(self.canvas, self.constraint_icon_20x20[constraint.type], 20)
                                drawn_icons.append(self.entity_and_constraint_to_drawn_constraint_icon[(point, constraint)])
                        else:
                            drawn_icons.append(self.entity_and_constraint_to_drawn_constraint_icon[(point, constraint)])

                icons_in_first_layer = 5
                first_layer_radius = 25
                layer = 0

                # number of icons in all layers from 0 to layer
                def helper(icons_in_first_layer, layer):
                    return (icons_in_first_layer * (layer + 2) * (layer + 1)) // 2

                offset = Vector(0, first_layer_radius)
                for i, drawn_icon in enumerate(drawn_icons):
                    drawn_icon.moveto(point + offset)
                    offset = offset.rotated(2 * pi / ((layer + 1) * icons_in_first_layer))
                    if (i > helper(icons_in_first_layer, layer) - 2):
                        layer += 1
                        offset += Vector(0, first_layer_radius)

class ConstraintIcon():
    def __init__(self, canvas, icon, icon_size):
        self.canvas = canvas
        center_point = Point(0, 0)
        self.background = self.create_rounded_rectangle(center_point.x - icon_size / 2, center_point.y - icon_size / 2, center_point.x + icon_size / 2, center_point.y + icon_size / 2, fill="pale green")
        self.icon = self.canvas.create_image((center_point.x, center_point.y), image = icon)
        self.icon_size = icon_size

    def moveto(self, point):
        self.canvas.moveto(self.background, int(point.x - self.icon_size // 2 - 1), int(point.y - self.icon_size // 2 - 1))
        self.canvas.moveto(self.icon, int(point.x - self.icon_size // 2), int(point.y - self.icon_size // 2))

    def set_background_color(self, color):
        self.canvas.itemconfig(self.background, fill = color)

    def create_rounded_rectangle(self, x1, y1, x2, y2, r = 10, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, \
            x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.canvas.create_polygon(points, **kwargs, smooth=True)
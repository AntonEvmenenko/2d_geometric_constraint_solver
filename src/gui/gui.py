import tkinter as tk
import tkinter.simpledialog
from gui.tooltip import ToolTip
from constraints.constraint import Constraint
from constraints.constraints import *
from examples.examples import examples
from geometry import Geometry
from geometric_primitives.point import Point, distance_p2p
from geometric_primitives.segment import Segment, distance_p2s
from math import atan2, degrees, pi
from geometric_primitives.arc import Arc, distance_p2a
from gui.constraint_icon import ConstraintIcon
from solver.solver import SOLVER_TYPE

WINDOW_SIZE = (840, 440)

USER_SELECTING_RADUIS   = 10

BUTTON_ICON_SIZE        = 32
CONSTRAINT_ICON_SIZE    = 20
CONSTRAINT_ICON_SPACING = 25
LINE_TICKNESS           = 3
POINT_RADIUS            = 4
TEXT_BOTTOM_OFFSET      = 15
TEXT_SIDE_OFFSET        = 15
MENU_TOP_OFFSET         = 10
MENU_SIDE_OFFSET        = 10


class GUI(tk.Frame):
    def __init__(self, root, geometry: Geometry, geometry_changed_callback, constraints, constraints_changed_callback, solver):
        tk.Frame.__init__(self, root)

        self.root = root

        self.geometry = geometry
        self.geometry_changed_callback = geometry_changed_callback

        self.constraints: Constraints = constraints
        self.constraints_changed_callback = constraints_changed_callback

        self.solver = solver

        self.canvas = tk.Canvas(self, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1], background='white', bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.entity_to_drawn_entity = {}
        self.entity_and_constraint_to_drawn_constraint_icon = {}

        self.selected_point = None
        self.selected_point_moved = False

        self.points_for_new_geometry = []
        self.adding_segment = False
        self.adding_arc = False

        self.degrees_of_freedom = 0

        # could be Segment, Arc, Point or Constraint
        self.selected_entities = set()

        self.zoom_scale = 1.0

        self.create_text_hint()
        self.create_text_info()
        self.create_side_menus()
        self.create_top_menu()
        self.create_bindings()
        self.create_icons()
        self.create_buttons()
        self.add_geometry()

    def create_text_hint(self):
        self.text_hint = tk.Label(self, bd=0, background='white')

    def create_text_info(self):
        self.text_info = tk.Label(self, bd=0, background='white')

    def set_text_hint(self, text):
        self.text_hint.config(text = text)

    def set_text_info(self, text):
        self.text_info.config(text = text)
        self.update()
        self.text_info.place(x = TEXT_SIDE_OFFSET, y = self.winfo_height() - self.text_info.winfo_height() - TEXT_BOTTOM_OFFSET)

    def solver_changed(self):
        selected_value = self.solver_type.get()
        new_solver_type = SOLVER_TYPE(selected_value)
        self.solver.set_solver_type(new_solver_type)

    def create_top_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff="off")
        file_menu.add_command(label='Clear', command=self.clear_everything)
        menubar.add_cascade(label="File", menu=file_menu)
        examples_menu = tk.Menu(menubar, tearoff="off")
        for example in examples:
            examples_menu.add_command(label=f'{example.__name__}', command=lambda example = example: self.load_example(example))
        menubar.add_cascade(label="Examples", menu=examples_menu)
        solver_menu = tk.Menu(menubar, tearoff="off")
        self.solver_type = tk.IntVar()
        self.solver_type.set(self.solver.solver_type.value)
        for s_type in SOLVER_TYPE:
            solver_menu.add_radiobutton(
                label=s_type.name,
                variable=self.solver_type,
                value=s_type.value,
                command=self.solver_changed
            )

        menubar.add_cascade(menu=solver_menu, label="Solver")

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
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)

        # windows zoom
        self.canvas.bind("<MouseWheel>",self.on_zoom)
        
        # resize of the main window
        self.bind("<Configure>", self.on_resize)

        self.root.bind("<KeyPress>", self.on_key_press)

    def create_icons(self):
        self.segment_icon = tk.PhotoImage(file = f"icons/{BUTTON_ICON_SIZE}x{BUTTON_ICON_SIZE}/segment.png")
        self.arc_icon =     tk.PhotoImage(file = f"icons/{BUTTON_ICON_SIZE}x{BUTTON_ICON_SIZE}/arc.png")
        self.circle_icon =  tk.PhotoImage(file = f"icons/{BUTTON_ICON_SIZE}x{BUTTON_ICON_SIZE}/circle.png")

        icon_sizes = [20, 32, 64, 128]

        self.constraint_icon = {}

        icon_file_name = {
            CONSTRAINT_TYPE.COINCIDENCE:            "coincidence",
            CONSTRAINT_TYPE.PARALLELITY:            "parallelity",
            CONSTRAINT_TYPE.PERPENDICULARITY:       "perpendicularity",
            CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS: "equal_length",
            CONSTRAINT_TYPE.FIXED:                  "fixed",
            CONSTRAINT_TYPE.HORIZONTALITY:          "horizontality",
            CONSTRAINT_TYPE.VERTICALITY:            "verticality",
            CONSTRAINT_TYPE.TANGENCY:               "tangency",
            CONSTRAINT_TYPE.CONCENTRICITY:          "concentricity",
            CONSTRAINT_TYPE.LENGTH:                 "length",
        }

        for icon_size in icon_sizes:
            self.constraint_icon[icon_size] = {}

            for constraint_type in CONSTRAINT_TYPE:
                self.constraint_icon[icon_size][constraint_type] = tk.PhotoImage(file = f"icons/{icon_size}x{icon_size}/{icon_file_name[constraint_type]}.png")

    def create_buttons(self):
        def create_menu_left_button(row, icon, command, hint_message):
            button = tk.Button(self.menu_left, image = icon, command = command, relief = tk.SOLID, bg = "light gray", activebackground = "light gray")
            button.grid(row = row, column = 1, sticky = "n", pady = 2)
            button.tooltip = ToolTip(button, hint_message, x_offset=30)

        create_menu_left_button(0, self.segment_icon, self.on_add_segment_button_clicked, "Segment (s)")
        create_menu_left_button(1, self.arc_icon, self.on_add_arc_button_clicked, "Arc (a)")
        # create_menu_left_button(2, self.circle_icon, None)

        def create_menu_right_constraint_button(row, constraint_type, hint_message=""):
            button = tk.Button(self.menu_right, image = self.constraint_icon[BUTTON_ICON_SIZE][constraint_type], \
                command = lambda: self.on_add_constraint_button_clicked(constraint_type), state=tk.DISABLED, relief = tk.SOLID, bg = "light gray", activebackground = "light gray")
            button.grid(row = row, column = 1, sticky="n", pady = 2)
            button.tooltip = ToolTip(button, hint_message, x_offset=-30)
            return button

        self.constraint_button = {
            CONSTRAINT_TYPE.COINCIDENCE:               create_menu_right_constraint_button(0, CONSTRAINT_TYPE.COINCIDENCE, "Coincidence (i)"),
            CONSTRAINT_TYPE.FIXED:                     create_menu_right_constraint_button(1, CONSTRAINT_TYPE.FIXED, "Fixed (f)"),
            CONSTRAINT_TYPE.PERPENDICULARITY:          create_menu_right_constraint_button(2, CONSTRAINT_TYPE.PERPENDICULARITY, "Perpendicularity (l)"),
            CONSTRAINT_TYPE.PARALLELITY:               create_menu_right_constraint_button(3, CONSTRAINT_TYPE.PARALLELITY, "Parallelity (b)"),
            CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS:    create_menu_right_constraint_button(4, CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS, "Equal (e)"),
            CONSTRAINT_TYPE.VERTICALITY:               create_menu_right_constraint_button(5, CONSTRAINT_TYPE.VERTICALITY, "Verticality (v)"),
            CONSTRAINT_TYPE.HORIZONTALITY:             create_menu_right_constraint_button(6, CONSTRAINT_TYPE.HORIZONTALITY, "Horizontality (h)"),
            CONSTRAINT_TYPE.TANGENCY:                  create_menu_right_constraint_button(7, CONSTRAINT_TYPE.TANGENCY, "Tangency (t)"),
            CONSTRAINT_TYPE.CONCENTRICITY:             create_menu_right_constraint_button(8, CONSTRAINT_TYPE.CONCENTRICITY, "Concentricity (o)"),
            CONSTRAINT_TYPE.LENGTH:                    create_menu_right_constraint_button(8, CONSTRAINT_TYPE.LENGTH, "Length (d)"),
        }

    # mouse and keyboard handlers

    def on_key_press(self, event):
        {
            'Delete': self.delete_selected_entities,
            's': self.on_add_segment_button_clicked,
            'a': self.on_add_arc_button_clicked,
            'i': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.COINCIDENCE),
            'f': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.FIXED),
            'l': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.PERPENDICULARITY),
            'b': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.PARALLELITY),
            'e': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.EQUAL_LENGTH_OR_RADIUS),
            'v': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.VERTICALITY),
            'h': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.HORIZONTALITY),
            't': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.TANGENCY),
            'o': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.CONCENTRICITY),
            'd': lambda: self.on_add_constraint_button_clicked(CONSTRAINT_TYPE.LENGTH),
            'p': self.print_detailed_info,
        }.get(event.keysym, lambda : None)()

    def on_left_button_pressed(self, event):
        canvas_cursor = Point(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        cursor = self.to_world(canvas_cursor)
        
        if self.adding_segment or self.adding_arc:
            self.points_for_new_geometry.append(cursor)

            self.set_text_hint(f'Select point {len(self.points_for_new_geometry) + 1}')

            if self.adding_segment and len(self.points_for_new_geometry) == 2:
                segment = Segment(self.points_for_new_geometry[0], self.points_for_new_geometry[1])
                self.geometry.segments.append(segment)
                self.add_drawn_entity(segment)
                self.new_geometry_added()
                return

            if self.adding_arc and len(self.points_for_new_geometry) == 3:
                arc = Arc(self.points_for_new_geometry[0], self.points_for_new_geometry[2], self.points_for_new_geometry[1])
                self.geometry.arcs.append(arc)
                self.add_drawn_entity(arc)
                self.new_geometry_added()
                return
            return

        for (_, constraint), drawn_constraint_icon in self.entity_and_constraint_to_drawn_constraint_icon.items():
            if cursor in drawn_constraint_icon:
                self.selected_entities.clear()
                self.selected_entities.add(constraint)
                self.redraw_geometry()
                return

        def unselect_constraints(selected_entities):
            constraints = set(filter(lambda entity: isinstance(entity, Constraint), selected_entities))
            return selected_entities - constraints

        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                if distance_p2p(point, cursor) < USER_SELECTING_RADUIS:
                    self.selected_point = point
                    self.selected_entities = unselect_constraints(self.selected_entities)
                    self.selected_entities.add(point)
                    self.check_constraints_requirements()
                    self.redraw_geometry()
                    return
            if isinstance(entity, Segment) and distance_p2s(cursor, entity) < USER_SELECTING_RADUIS:
                self.selected_entities = unselect_constraints(self.selected_entities)
                self.selected_entities.add(entity)
                self.check_constraints_requirements()
                self.redraw_geometry()
                return

            if isinstance(entity, Arc) and distance_p2a(cursor, entity) < USER_SELECTING_RADUIS:
                if entity in self.selected_entities: # "double click"
                    entity.invert_direction()
                self.selected_entities = unselect_constraints(self.selected_entities)
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
            if (constraint.type == CONSTRAINT_TYPE.FIXED) and (self.selected_point in constraint.entities):
                return

        self.selected_point_moved = True

        canvas_cursor = Point(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        cursor = self.to_world(canvas_cursor)

        self.selected_point.x, self.selected_point.y = cursor.x, cursor.y

        self.geometry_changed_callback(self.selected_point)

    def on_middle_mouse_button_pressed(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_middle_mouse_button_released(self, event):    
        pass
    
    def on_middle_mouse_button_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_zoom(self, event):
        if event.num == 5 or event.delta < 0:
            factor = 0.9
        else:
            factor = 1.1

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.zoom_scale *= factor

        shift_x = x * (factor - 1)
        shift_y = y * (factor - 1)

        self.canvas.scan_mark(0, 0)
        self.canvas.scan_dragto(int(-shift_x), int(-shift_y), gain=1)

        self.redraw_geometry()

    def to_screen(self, p):
        return Point(p.x * self.zoom_scale, p.y * self.zoom_scale)

    def to_world(self, p):
        return Point(p.x / self.zoom_scale, p.y / self.zoom_scale)

    # external events handlers

    def on_resize(self, event, repeat = True):
        self.canvas.config(width = event.width, height = event.height)
        
        self.menu_left.place(x = MENU_SIDE_OFFSET, y = MENU_TOP_OFFSET)
        self.menu_right.place(x = event.width - self.menu_right.winfo_width() - MENU_SIDE_OFFSET, y = MENU_TOP_OFFSET)

        self.text_hint.place(x = TEXT_SIDE_OFFSET, y = event.height - self.text_hint.winfo_height() - TEXT_BOTTOM_OFFSET)

        self.redraw_geometry()

        if repeat:
            self.update()
            self.on_resize(event, False)

    # screen buttons handlers

    def on_add_segment_button_clicked(self):
        self.set_text_hint('Select point 1')
        self.adding_segment = True

    def on_add_arc_button_clicked(self):
        self.set_text_hint('Select point 1')
        self.adding_arc = True

    def on_add_constraint_button_clicked(self, constraint_type):
        if constraint_type == CONSTRAINT_TYPE.LENGTH:
            new_length = tkinter.simpledialog.askinteger("Input", "Enter the length", parent=self.root)
            if not new_length is None:
                self.add_constraint(Constraint([list(self.selected_entities)[0], new_length], constraint_type))
        else:
            self.add_constraint(Constraint(list(self.selected_entities), constraint_type))

        self.selected_entities.clear()
        self.check_constraints_requirements()
        self.constraints_changed_callback()

    # elements drawing (geometry)

    def add_drawn_point(self, point):
        return self.canvas.create_oval(point.x - POINT_RADIUS, point.y - POINT_RADIUS, point.x + POINT_RADIUS, point.y + POINT_RADIUS, fill='blue', outline='blue')

    def remove_drawn_point(self, point: Point):
        self.canvas.delete(self.entity_to_drawn_entity[point])
        self.entity_to_drawn_entity.pop(point, None)

    def add_drawn_segment(self, segment: Segment):
        line = self.canvas.create_line(segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y, capstyle=tk.ROUND, joinstyle=tk.ROUND, width=LINE_TICKNESS)
        self.canvas.tag_lower(line)
        self.entity_to_drawn_entity[segment] = line

        self.entity_to_drawn_entity[segment.p1] = self.add_drawn_entity(segment.p1)
        self.entity_to_drawn_entity[segment.p2] = self.add_drawn_entity(segment.p2)

    def remove_drawn_segment(self, segment: Segment):
        self.canvas.delete(self.entity_to_drawn_entity[segment])
        self.entity_to_drawn_entity.pop(segment, None)
        self.remove_drawn_entity(segment.p1)
        self.remove_drawn_entity(segment.p2)

    def calculate_arc_start_and_extent(self, arc: Arc):
        arc_center = arc.center()

        center_p2 = Vector.from_two_points(arc_center, arc.p2)
        center_p1 = Vector.from_two_points(arc_center, arc.p1)

        start_angle = degrees(atan2(-center_p1.y, center_p1.x))
        end_angle = degrees(atan2(-center_p2.y, center_p2.x))

        if start_angle < end_angle:
            start_angle += 360

        extent = end_angle - start_angle

        return start_angle, extent

    def add_drawn_arc(self, arc: Arc):
        bb_coords = arc.bb_coords()

        start, extent = self.calculate_arc_start_and_extent(arc)

        drawn_arc = self.canvas.create_arc(bb_coords, start = start, extent = extent, style=tk.ARC, width=LINE_TICKNESS)
        self.canvas.tag_lower(drawn_arc)
        self.entity_to_drawn_entity[arc] = drawn_arc 

        self.entity_to_drawn_entity[arc.p1] = self.add_drawn_entity(arc.p1)
        self.entity_to_drawn_entity[arc.p2] = self.add_drawn_entity(arc.p2)

    def remove_drawn_arc(self, arc: Arc):
        self.canvas.delete(self.entity_to_drawn_entity[arc])
        self.entity_to_drawn_entity.pop(arc, None)
        self.remove_drawn_entity(arc.p1)
        self.remove_drawn_entity(arc.p2)

    def remove_drawn_entity(self, entity):
        {
            Arc:        self.remove_drawn_arc,
            Segment:    self.remove_drawn_segment,
            Point:      self.remove_drawn_point,
        }.get(entity.__class__, lambda : None)(entity)

    def add_drawn_entity(self, entity):
        return {
            Arc:        self.add_drawn_arc,
            Segment:    self.add_drawn_segment,
            Point:      self.add_drawn_point,
        }.get(entity.__class__, lambda : None)(entity)

    def add_geometry(self):
        for entity in (self.geometry.segments + self.geometry.arcs):
            self.add_drawn_entity(entity)

    def remove_geometry(self):
        for entity in (self.geometry.segments + self.geometry.arcs):
            self.remove_drawn_entity(entity)

    def redraw_geometry(self):
        # segments and arcs
        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                screen_p = self.to_screen(point)
                self.canvas.coords(self.entity_to_drawn_entity[point], 
                                   screen_p.x - POINT_RADIUS, screen_p.y - POINT_RADIUS, 
                                   screen_p.x + POINT_RADIUS, screen_p.y + POINT_RADIUS)
                self.canvas.itemconfig(self.entity_to_drawn_entity[point], fill='blue', outline='blue')

            line_color = "red" if entity in self.selected_entities else "black"
            self.canvas.itemconfig(self.entity_to_drawn_entity[entity], fill=line_color)
            if isinstance(entity, Arc):
                self.canvas.itemconfig(self.entity_to_drawn_entity[entity], outline=line_color)

        # segments
        for segment in self.geometry.segments:
            p1_s = self.to_screen(segment.p1)
            p2_s = self.to_screen(segment.p2)
            self.canvas.coords(self.entity_to_drawn_entity[segment], p1_s.x, p1_s.y, p2_s.x, p2_s.y)

        # arcs
        for arc in self.geometry.arcs:
            bb = arc.bb_coords()
            scaled_bb = (bb[0] * self.zoom_scale, bb[1] * self.zoom_scale, 
                         bb[2] * self.zoom_scale, bb[3] * self.zoom_scale)
            self.canvas.coords(self.entity_to_drawn_entity[arc], *scaled_bb)
            start, extent = self.calculate_arc_start_and_extent(arc)
            self.canvas.itemconfig(self.entity_to_drawn_entity[arc], start = start, extent = extent)

        # selected points
        for selected_point in [entity for entity in self.selected_entities if isinstance(entity, Point)]:
            circle = self.entity_to_drawn_entity[selected_point]
            self.canvas.itemconfig(circle, fill='red', outline='red')
            self.canvas.tag_raise(circle)

        # constraint icons
        for (_, constraint), drawn_constraint_icon in self.entity_and_constraint_to_drawn_constraint_icon.items():
            color = "red" if constraint in self.selected_entities else "pale green"
            drawn_constraint_icon.set_background_color(color)

        self.update_constraint_icons()
        self.set_text_info(f'e: {len(self.geometry.segments) + len(self.geometry.arcs)} | c: {len(self.constraints)} | d: {self.degrees_of_freedom}')

    # elements drawing (constraints)

    def add_constraint_icon(self, constraint):
        for entity in (self.geometry.segments + self.geometry.arcs):
            if entity in constraint.entities:
                if not (entity, constraint) in self.entity_and_constraint_to_drawn_constraint_icon:
                    icon = constraint.entities[1] if constraint.type == CONSTRAINT_TYPE.LENGTH else self.constraint_icon[CONSTRAINT_ICON_SIZE][constraint.type]
                    self.entity_and_constraint_to_drawn_constraint_icon[(entity, constraint)] = ConstraintIcon(self.canvas, icon, CONSTRAINT_ICON_SIZE)

            for point in entity.points():
                if point in constraint.entities:
                    if not (point, constraint) in self.entity_and_constraint_to_drawn_constraint_icon:
                        exists_already = (constraint.type == CONSTRAINT_TYPE.COINCIDENCE) and any(c is constraint for (p, c) in self.entity_and_constraint_to_drawn_constraint_icon)
                        if not exists_already:
                            self.entity_and_constraint_to_drawn_constraint_icon[(point, constraint)] = ConstraintIcon(self.canvas, self.constraint_icon[CONSTRAINT_ICON_SIZE][constraint.type], CONSTRAINT_ICON_SIZE)

    def remove_constraint_icon(self, constraint):
        def remove_icon(entity):
            icon = self.entity_and_constraint_to_drawn_constraint_icon.get((entity, constraint))
            if not icon is None:
                icon.remove_drawn_entities()
                self.entity_and_constraint_to_drawn_constraint_icon.pop((entity, constraint), None)

        for entity in (self.geometry.segments + self.geometry.arcs):
            if entity in constraint.entities:
                remove_icon(entity)

            for point in entity.points():
                if point in constraint.entities:
                    remove_icon(point)

    def add_constraint_icons(self):
        for constraint in self.constraints:
            self.add_constraint_icon(constraint)

    def remove_constraint_icons(self):
        for constraint in self.constraints:
            self.remove_constraint_icon(constraint)

    def update_constraint_icons(self):
        # constraint icons for segments and arcs
        for entity in (self.geometry.segments + self.geometry.arcs):
            drawn_icons = []

            for constraint in self.constraints:
                if entity in constraint.entities:
                    drawn_icons.append(self.entity_and_constraint_to_drawn_constraint_icon[(entity, constraint)])

            normal_spacing = CONSTRAINT_ICON_SPACING
            tangent_spacing = normal_spacing + 10

            if isinstance(entity, Segment):
                tangent_offset = max(tangent_spacing * (len(drawn_icons) - 1), 0) / 2

                p1_p2 = Vector.from_two_points(entity.p1, entity.p2)
                p1_p2_unit = p1_p2.normalized()

                center_point_world = entity.p1 + p1_p2 / 2
                center_point_screen = self.to_screen(center_point_world)

                n = Vector(p1_p2_unit.y, -p1_p2_unit.x)

                for i, drawn_icon in enumerate(drawn_icons):
                    drawn_icon.moveto(center_point_screen + n * normal_spacing + p1_p2_unit * (-tangent_offset) + p1_p2_unit * (i * tangent_spacing))

            elif isinstance(entity, Arc):
                center = entity.center()
                radius = entity.radius()
                middle = entity.middle_point()

                c_m_unit = Vector.from_two_points(center, middle).normalized()

                radius_screen = radius * self.zoom_scale
                center_screen = self.to_screen(center)

                delta_angle = tangent_spacing / (radius_screen + normal_spacing)
                angle_offset = max(delta_angle * (len(drawn_icons) - 1), 0) / 2

                for i, drawn_icon in enumerate(drawn_icons):
                    drawn_icon.moveto(center_screen + (c_m_unit * (radius_screen + normal_spacing)).rotated(-angle_offset + delta_angle * i))

        # constraint icons for points
        for entity in (self.geometry.segments + self.geometry.arcs):
            for point in entity.points():
                drawn_icons = []

                for constraint in self.constraints:
                    if point in constraint.entities:
                        if (point, constraint) in self.entity_and_constraint_to_drawn_constraint_icon:
                            drawn_icons.append(self.entity_and_constraint_to_drawn_constraint_icon[(point, constraint)])

                icons_in_first_layer = 5
                first_layer_radius = CONSTRAINT_ICON_SPACING
                layer = 0
                # number of icons in all layers from 0 to layer
                def helper(icons_in_first_layer, layer):
                    return (icons_in_first_layer * (layer + 2) * (layer + 1)) // 2

                offset = Vector(0, first_layer_radius)

                point_screen = self.to_screen(point)

                for i, drawn_icon in enumerate(drawn_icons):
                    drawn_icon.moveto(point_screen + offset)
                    offset = offset.rotated(2 * pi / ((layer + 1) * icons_in_first_layer))
                    if (i > helper(icons_in_first_layer, layer) - 2):
                        layer += 1
                        offset += Vector(0, first_layer_radius)

    # misc

    def add_constraint(self, constraint: Constraint):
        new_constraints = self.constraints.add_constraint(constraint.type, constraint.entities)
        for constraint in new_constraints:
            self.add_constraint_icon(constraint)

    def remove_constraint(self, constraint: Constraint):
        self.remove_constraint_icon(constraint)
        self.constraints.remove(constraint)

    def new_geometry_added(self):
        self.points_for_new_geometry.clear()

        self.adding_segment = False
        self.adding_arc = False
        
        self.set_text_hint("")

        self.geometry_changed_callback(None)

    def check_constraints_requirements(self):
        for button in self.constraint_button.values():
            button.configure(state = tk.DISABLED)

        for constraint_type in Constraints.get_available_constraints(self.selected_entities):
            self.constraint_button[constraint_type].configure(state = tk.NORMAL)

    def clear_everything(self):
        self.remove_geometry()
        self.remove_constraint_icons()
        self.geometry.clear()
        self.constraints.clear()

    def load_example(self, example):
        self.clear_everything()
        example(self.geometry, self.constraints)
        self.add_geometry()
        self.add_constraint_icons()
        self.constraints_changed_callback()

    def delete_selected_entities(self):
        entities_to_be_removed = []

        for entity in list(self.selected_entities):
            arc, segment = isinstance(entity, Arc), isinstance(entity, Segment)

            if arc or segment:
                self.remove_drawn_entity(entity)
                entities_to_be_removed.append(entity)
                entities_to_be_removed.append(entity.p1)
                entities_to_be_removed.append(entity.p2)
                self.selected_entities.remove(entity)

        useless_constraints = self.constraints.get_useless_constraints(entities_to_be_removed)
        constraints_to_be_removed = set(filter(lambda entity: isinstance(entity, Constraint), self.selected_entities))

        for constraint in (constraints_to_be_removed.union(useless_constraints)):
            self.remove_constraint(constraint)

        for entity in entities_to_be_removed:
            self.geometry.remove_entity(entity)

        self.selected_entities.clear()

        self.geometry_changed_callback(None)
        self.constraints_changed_callback()
        self.redraw_geometry()

    def print_detailed_info(self):
        print ("")
        print ("==============================")
        print (f"Constraints [{len(self.constraints)}]:")
        print (f"\tFixed: {self.constraints.fixed_constraints}")
        print (f"\tInactive: {self.constraints.inactive_constraints}")
        print (f"\tSolved by substitution: {self.constraints.solved_by_substitution_constraints}")
        print (f"\tSolved by solver: {len(self.constraints) - self.constraints.solved_by_substitution_constraints - self.constraints.fixed_constraints}")
        print ("==============================")
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, x_offset, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay       # Delay in milliseconds
        self.x_offset = x_offset # Offset from the button center
        self.tipwindow = None
        self.id = None           # Timer ID

        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<ButtonPress>", self.hide_tip)

    def schedule_show(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tip(self, event=None):
        # 1. Create the window invisible first
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        
        # Mac OS fix
        try:
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "noActivates")
        except tk.TclError:
            pass

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

        # 2. Update to get accurate dimensions of the generated tooltip
        tw.update_idletasks()
        
        # 3. Get dimensions
        tip_w = tw.winfo_width()
        tip_h = tw.winfo_height()
        
        btn_x = self.widget.winfo_rootx()
        btn_y = self.widget.winfo_rooty()
        btn_w = self.widget.winfo_width()
        btn_h = self.widget.winfo_height()

        # Calculate Button Center
        btn_center_x = btn_x + (btn_w // 2)
        btn_center_y = btn_y + (btn_h // 2)

        # 4. Calculate X Position based on offset sign
        if self.x_offset >= 0:
            # Positive: Start 'x_offset' pixels to the right of the center
            x = btn_center_x + self.x_offset
        else:
            # Negative: End 'x_offset' pixels to the left of the center.
            # Since Tkinter places windows by Top-Left, we subtract the tooltip width.
            x = (btn_center_x + self.x_offset) - tip_w

        # 5. Calculate Y Position (Vertically Centered)
        y = btn_center_y - (tip_h // 2)

        tw.wm_geometry(f"+{x}+{y}")

    def hide_tip(self, event=None):
        self.unschedule()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
import tkinter as tk


class ToolTip:
    @staticmethod
    def for_widget(widget, text):
        ToolTip(widget, text)

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.move_tooltip)

    def show_tooltip(self, event):
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Removes borders
        self.update_position(event)
        label = tk.Label(self.tooltip_window, text=self.text, background="light yellow", relief="solid", borderwidth=1,
                         font=("Arial", 10))
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def move_tooltip(self, event):
        self.update_position(event)

    def update_position(self, event):
        x = event.x_root + 10
        y = event.y_root + 15

        self.tooltip_window.wm_geometry(f"+{x}+{y}")

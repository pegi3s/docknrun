import tkinter as tk


# Clase Tooltip para crear el mensaje emergente
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
        self.widget.bind("<Motion>", self.move_tooltip)  # Detectar movimiento del ratón

    def show_tooltip(self, event):
        # Crear una nueva ventana Toplevel para el tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Eliminar bordes
        self.update_position(event)  # Posicionar el tooltip inicialmente
        label = tk.Label(self.tooltip_window, text=self.text, background="light yellow", relief="solid", borderwidth=1,
                         font=("Arial", 10))
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def move_tooltip(self, event):
        # Actualizar la posición del tooltip para que siga al ratón
        self.update_position(event)

    def update_position(self, event):
        # Posicionar el tooltip en las coordenadas actuales del ratón
        x = event.x_root + 10
        y = event.y_root + 15
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

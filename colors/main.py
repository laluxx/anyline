import os
import gi
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gi.repository import Gtk, Gdk, GLib

CONFIG = {
    'update_interval': 500,  # Update interval for the plot in milliseconds
    'border_width': 2,       # Border width for the grid
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class ColorGridWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(100, 24)  # Adjust size here as needed
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(850, 0)  # Adjust position here as needed

        self.fig, self.ax = plt.subplots(figsize=(30,2.4), dpi=10)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(100, 24)
        self.add(self.canvas)

        self.update_colors()

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))

    def lighten_color(self, color, factor=0.4):
        return tuple(min(1, c + factor) for c in color)

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color) for color in color_lines]

        if self.colors:
            self.fig.patch.set_facecolor(self.colors[0])

        self.update_plot()

    def update_plot(self):
        self.ax.clear()

        for i, color in enumerate(self.colors):
            row, col = divmod(i, 8)
            rect = Rectangle((col, 1-row), 1, 1, facecolor=color, edgecolor=None)
            self.ax.add_patch(rect)

        border_color = self.lighten_color(self.colors[0])
        border = Rectangle((0, 0), 8, 2, fill=False, edgecolor=border_color, linewidth=CONFIG['border_width'])
        self.ax.add_patch(border)

        self.ax.set_xlim([0, 8])
        self.ax.set_ylim([0, 2])
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.axis('off')

        self.canvas.draw_idle()

        GLib.timeout_add(CONFIG['update_interval'], self.update_plot)

    def run(self):
        observer = Observer()
        event_handler = MyHandler(self)
        observer.schedule(event_handler, path=os.path.expanduser('~/.cache/wal'), recursive=False)
        observer.start()

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    colorGridWindow = ColorGridWindow()
    colorGridWindow.run()


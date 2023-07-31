#!/usr/bin/env python3

# MAIN
import os
import gi
import psutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.patches import Rectangle
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gi.repository import Gtk, Gdk, GLib

CONFIG = {
    'update_interval': 500,  # Update interval for the plot in milliseconds
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class CoreActivityWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(60, 24)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(850, 0)  # Adjust position here as needed

        self.fig, self.ax = plt.subplots(figsize=(6,3), dpi=10)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(60, 24)
        self.add(self.canvas)

        self.update_colors()

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color) for color in color_lines]

        if self.colors:
            self.fig.patch.set_facecolor(self.colors[0])

        self.update_plot()

    def update_plot(self):
        self.ax.clear()

        core_usage = psutil.cpu_percent(interval=0.1, percpu=True)
        grid_size = int(np.ceil(np.sqrt(len(core_usage))))
        usage_grid = np.array(core_usage).reshape((grid_size, -1))

        for (j, i), usage in np.ndenumerate(usage_grid):
            color_index = min(int(usage // 7), len(self.colors) - 1)  # divide usage by 7 to get an index in the color range
            color = self.colors[color_index]
            rect = Rectangle((i, j), 1, 1, facecolor=color, edgecolor='white', linewidth=0.1)
            self.ax.add_patch(rect)

        self.ax.set_xlim([0, grid_size])
        self.ax.set_ylim([0, grid_size])
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
    coreActivityWindow = CoreActivityWindow()
    coreActivityWindow.run()

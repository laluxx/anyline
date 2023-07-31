#!/usr/bin/env python3

import os
import gi
import psutil
from gi.repository import Gtk, Gdk, GLib
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.patches import Wedge
from matplotlib.colors import LinearSegmentedColormap
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import matplotlib.pyplot as plt

CONFIG = {
    'update_interval': 500,  # Update interval for the plot in milliseconds
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class SystemUsageWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(120, 60)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(850, 0)

        self.fig, self.axs = plt.subplots(1, 2, figsize=(12,6), dpi=10)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(120, 60)
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
        for ax in self.axs:
            ax.clear()

        # Draw RAM usage pie
        memory = psutil.virtual_memory()
        used_ram_percent = memory.percent
        cmap = LinearSegmentedColormap.from_list("wal", self.colors[1:9])
        ram_wedge = Wedge((0.5, 0.5), 0.5, -90, used_ram_percent * 3.6 - 90, transform=self.axs[0].transAxes, cmap=cmap)
        self.axs[0].add_patch(ram_wedge)

        # Draw Disk usage pie
        disk = psutil.disk_usage('/')
        used_disk_percent = disk.percent
        cmap = LinearSegmentedColormap.from_list("wal", self.colors[9:])
        disk_wedge = Wedge((0.5, 0.5), 0.5, -90, used_disk_percent * 3.6 - 90, transform=self.axs[1].transAxes, cmap=cmap)
        self.axs[1].add_patch(disk_wedge)

        for ax in self.axs:
            ax.set_xlim([0, 1])
            ax.set_ylim([0, 1])
            ax.axis('off')

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
    systemUsageWindow = SystemUsageWindow()
    systemUsageWindow.run()

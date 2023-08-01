#!/usr/bin/env python3

import os
import gi
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gi.repository import Gtk, Gdk, GLib

CONFIG = {
    'window_width': 60,
    'window_height': 60,
    'window_pos_x': 850,
    'window_pos_y': 0,
    'update_interval': 1000,  # Update interval for the plot in milliseconds
    'colors_index': 1,  # The color index to use for the plot
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class ClockWindow(Gtk.Window):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="ClockWindow", application=app)

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(CONFIG['window_width'], CONFIG['window_height'])

        self.fig, self.ax = plt.subplots(figsize=(CONFIG['window_width']/10, CONFIG['window_height']/10), dpi=10)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(CONFIG['window_width'], CONFIG['window_height'])
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

        current_time = dt.datetime.now().time()
        hours = current_time.hour
        minutes = current_time.minute
        seconds = current_time.second

        self.ax.pie([hours/24, 1-hours/24], colors=[self.colors[CONFIG['colors_index']], self.colors[0]], startangle=90)
        self.ax.pie([minutes/60, 1-minutes/60], colors=[self.colors[CONFIG['colors_index']+1], self.colors[0]], startangle=90)
        self.ax.pie([seconds/60, 1-seconds/60], colors=[self.colors[CONFIG['colors_index']+2], self.colors[0]], startangle=90)

        self.ax.axis('equal')

        self.canvas.draw_idle()

        GLib.timeout_add(CONFIG['update_interval'], self.update_plot)

class ClockApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = ClockWindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = ClockApp()
exit_status = app.run(None)

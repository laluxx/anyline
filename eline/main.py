#!/usr/bin/env python3

import gi
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from gi.repository import Gtk, Gdk, GLib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG = {
    'update_interval': 1000,  # Update interval for the plot in milliseconds
    'color': 4,  # The index of the color in the pywal color scheme to use
    'window_width': 90,  # The width of the window
    'window_height': 26,  # The height of the window
    'window_pos_x': 1000,  # The x-coordinate of the window position
    'window_pos_y': 0,  # The y-coordinate of the window position
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)
        elif event.src_path == '/tmp/emacs-buffer-list':
            GLib.idle_add(self.overlay.update_buffers)

class EmacsBuffersWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(CONFIG['window_width'], CONFIG['window_height'])
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(CONFIG['window_pos_x'], CONFIG['window_pos_y'])

        self.buffer_list = []
        self.current_buffer = None

        self.fig, self.ax = plt.subplots(figsize=(6,3), dpi=10)
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

    def update_buffers(self):
        with open('/tmp/emacs-buffer-list', 'r') as f:
            lines = f.read().splitlines()
            try:
                separator_index = lines.index('----')
                self.buffer_list = lines[:separator_index]
                self.current_buffer = lines[separator_index + 1]
            except ValueError:
                print("Warning: '----' separator not found in '/tmp/emacs-buffer-list' file")
                return

        self.update_plot()

    def update_plot(self):
        self.ax.clear()

        num_buffers = len(self.buffer_list)
        if num_buffers > 0:
            self.ax.pie(
                [1]*num_buffers,
                colors=[self.colors[CONFIG['color']] if buffer == self.current_buffer else self.colors[0] for buffer in self.buffer_list],
                startangle=90,
                counterclock=False
            )

            self.ax.axis('equal')

            self.canvas.draw_idle()

        GLib.timeout_add(CONFIG['update_interval'], self.update_plot)

    def run(self):
        observer = Observer()
        event_handler = MyHandler(self)
        observer.schedule(event_handler, path=os.path.expanduser('~/.cache/wal'), recursive=False)
        observer.schedule(event_handler, path='/tmp/emacs-buffer-list', recursive=False)
        observer.start()

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    emacsBuffersWindow = EmacsBuffersWindow()
    emacsBuffersWindow.run()

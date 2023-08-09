#!/usr/bin/env python3

# TODO:
# make it use the same color as xmobar [x]

import os
import gi
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gi.repository import Gtk, Gdk, GLib

CONFIG = {
    'update_interval': 1000,  # Update interval for the plot in milliseconds
    'color': 4,  # The index of the color in the pywal color scheme to use
    'window_width': 30,  # The width of the window
    'window_height': 18,  # The height of the window
    'window_pos_x': 1166,  # The x-coordinate of the window position
    'window_pos_y': 0,  # The y-coordinate of the window position
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class MemoryPieWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(CONFIG['window_width'], CONFIG['window_height'])
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(CONFIG['window_pos_x'], CONFIG['window_pos_y'])

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

    def update_plot(self):
        self.ax.clear()

        memory = psutil.virtual_memory()
        used_memory = memory.percent
        unused_memory = 100 - used_memory

        self.ax.pie(
            [used_memory, unused_memory],
            colors=[self.colors[CONFIG['color']], self.colors[0]],
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
        observer.start()

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    memoryPieWindow = MemoryPieWindow()
    memoryPieWindow.run()





























# MAIN
#!/usr/bin/env python3
# import os
# import gi
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from gi.repository import Gtk, Gdk, GLib

# CONFIG = {
#     'update_interval': 1000,  # Update interval for the plot in milliseconds
#     'color_index': 1,  # Choose color from wal colors
# }

# class MyHandler(FileSystemEventHandler):
#     def __init__(self, overlay):
#         self.overlay = overlay

#     def on_modified(self, event):
#         if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
#             GLib.idle_add(self.overlay.update_colors)

# class PieChartWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()

#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(60, 24)  # Adjust size here as needed
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(850, 0)  # Adjust position here as needed

#         self.fig, self.ax = plt.subplots(figsize=(6,3), dpi=10)
#         self.canvas = FigureCanvas(self.fig)
#         self.add(self.canvas)

#         self.update_colors()

#     def hex_to_rgb(self, color):
#         color = color.lstrip('#')
#         return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))

#     def update_colors(self):
#         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
#             color_lines = [line.strip() for line in f]
#             self.colors = [self.hex_to_rgb(color) for color in color_lines]

#         if self.colors:
#             self.fig.patch.set_facecolor(self.colors[0])

#         self.update_plot()

#     def update_plot(self):
#         self.ax.clear()

#         # Add your data here
#         data = [5, 3, 4, 2]

#         wedges, _ = self.ax.pie(data, colors=[self.colors[CONFIG['color_index']]], startangle=90, wedgeprops=dict(width=0.4))

#         for w in wedges:
#             w.set_edgecolor(self.colors[0])

#         self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

#         self.canvas.draw_idle()

#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)

#     def run(self):
#         observer = Observer()
#         event_handler = MyHandler(self)
#         observer.schedule(event_handler, path=os.path.expanduser('~/.cache/wal'), recursive=False)
#         observer.start()

#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()

# if __name__ == "__main__":
#     pieChartWindow = PieChartWindow()
#     pieChartWindow.run()

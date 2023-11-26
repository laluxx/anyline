import os
import gi
import psutil
import numpy as np
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from gi.repository import Gtk, Gdk, GLib
import collections
from scipy.interpolate import CubicSpline

CONFIG = {
    'buffer_size': 60,
    'update_interval': 1000,
    'color_indices': [0, 3, 6, 9],
    'num_points': 50,
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class NetworkStatWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.colors = []
        self.previous_net_stats = psutil.net_io_counters()
        self.net_stats_buffer = collections.deque([0]*CONFIG['buffer_size'], maxlen=CONFIG['buffer_size'])

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(474, 22)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(1426, 0)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(474, 23)

        self.add(self.canvas)

        self.update_colors()
        self.update_plot()

        # Connect to the realize signal
        self.connect("realize", self.on_realize)

    def on_realize(self, widget):
        gdk_window = widget.get_window()
        if gdk_window:
            gdk_window.set_override_redirect(True)

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color_lines[i]) for i in CONFIG['color_indices']]

        if self.colors:
            self.fig.patch.set_facecolor(self.colors[0])

    def update_plot(self):
        self.ax.clear()

        current_net_stats = psutil.net_io_counters()
        net_stats_diff = [curr - prev for curr, prev in zip(current_net_stats, self.previous_net_stats)]
        self.previous_net_stats = current_net_stats

        self.net_stats_buffer.append(sum(net_stats_diff))

        x = np.linspace(0, CONFIG['num_points'], num=len(self.net_stats_buffer), endpoint=True)
        y = np.array(self.net_stats_buffer)

        cs = CubicSpline(x, y)
        xs = np.linspace(0, CONFIG['num_points'], num=1000, endpoint=True)

        if len(self.colors) > 1:
            color = self.colors[1]
        else:
            color = 'b'

        self.ax.plot(xs, cs(xs), color=color)

        self.ax.set_facecolor(self.colors[0])
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
    networkStatWindow = NetworkStatWindow()
    networkStatWindow.run()

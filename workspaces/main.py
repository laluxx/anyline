#!/usr/bin/env python3




import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking("type='signal',interface='org.xmonad.Log',member='Update'")

def handle_signal(*args, **kwargs):
    # This function will be called whenever the 'Update' signal is emitted.
    # The workspace information will be contained in the 'args' parameter.
    print(args)

bus.add_message_filter(handle_signal)

loop = GLib.MainLoop()
loop.run()





# import os
# import gi
# import time
# import subprocess
# import matplotlib.pyplot as plt
# from matplotlib.patches import Circle
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from gi.repository import Gtk, Gdk, GLib
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
#
# CONFIG = {
#     'update_interval': 500,  # Update interval for the plot in milliseconds
#     'color': 4,  # The index of the color in the pywal color scheme to use
#     'window_width': 300,  # The width of the window
#     'window_height': 300,  # The height of the window
#     'window_pos_x': 1166,  # The x-coordinate of the window position
#     'window_pos_y': 0,  # The y-coordinate of the window position
# }
#
# class MyHandler(FileSystemEventHandler):
#     def __init__(self, overlay):
#         self.overlay = overlay
#
#     def on_modified(self, event):
#         if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
#             GLib.idle_add(self.overlay.update_colors)
#
# class WorkspaceWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(CONFIG['window_width'], CONFIG['window_height'])
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(CONFIG['window_pos_x'], CONFIG['window_pos_y'])
#
#         self.fig, self.ax = plt.subplots(figsize=(6,6), dpi=50)
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.set_size_request(CONFIG['window_width'], CONFIG['window_height'])
#         self.add(self.canvas)
#
#         self.update_colors()
#
#     def hex_to_rgb(self, color):
#         color = color.lstrip('#')
#         return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))
#
#     def update_colors(self):
#         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
#             color_lines = [line.strip() for line in f]
#             self.colors = [self.hex_to_rgb(color) for color in color_lines]
#
#         if self.colors:
#             self.fig.patch.set_facecolor(self.colors[0])
#
#         self.update_plot()
#
#
#     def update_plot(self):
#         self.ax.clear()
#         self.ax.set_xlim(-5,5)
#         self.ax.set_ylim(-5,5)
#
#         # Wait until the file exists
#         while not os.path.exists("/tmp/workspace_info.txt"):
#             print("Waiting for workspace info file...")
#             time.sleep(0.5)
#
#         with open("/tmp/workspace_info.txt", "r") as f:
#             workspace_lines = [line.strip() for line in f]
#
#         for i, line in enumerate(workspace_lines[:9]):
#             tag, status = line.split(" ")
#             filled = (status == "*")
#             circle = Circle((i-4, 0), 0.5, fill=filled, color=self.colors[CONFIG['color']])
#             self.ax.add_patch(circle)
#
#         self.ax.axis('equal')
#         self.canvas.draw_idle()
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
#
#     def run(self):
#         # Add these lines to run the Haskell script when the Python script starts
#         print("Running Haskell script...")
#         try:
#             subprocess.check_call(["ghc", "-e", "main", "fetch-workspaces.hs"])
#         except subprocess.CalledProcessError:
#             print("Failed to execute Haskell script.")
#             return
#         print("Haskell script executed successfully.")
#
#         observer = Observer()
#         event_handler = MyHandler(self)
#         observer.schedule(event_handler, path=os.path.expanduser('~/.cache/wal'), recursive=False)
#         observer.start()
#
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()
#
# if __name__ == "__main__":
#     workspaceWindow = WorkspaceWindow()
#     workspaceWindow.run()

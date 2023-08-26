#!/usr/bin/env python3

# FINALLY WORK
import os
import gi
gi.require_version('Gtk', '3.0')
import numpy as np
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG = {
    'update_interval': 5000,
    'github_username': 'laluxx',
    'window_position_x': 870,
    'window_position_y': 0,
    'personal_access_token': ''
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class GitHubContributionsWindow(Gtk.Window):
    def __init__(self):
        super(GitHubContributionsWindow, self).__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(-1, 24)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(CONFIG['window_position_x'], CONFIG['window_position_y'])

        self.image = Gtk.Image()
        self.add(self.image)

        self.update_colors()

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color) for color in color_lines]

        rgba = Gdk.RGBA(*[c/255.0 for c in self.colors[0]], 1.0)
        self.override_background_color(Gtk.StateFlags.NORMAL, rgba)

        self.update_plot()

    def fetch_contributions(self):
        headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
        json = {
            "query": """query($userName:String!) {user(login: $userName){
                       contributionsCollection {contributionCalendar {
                       totalContributions weeks {contributionDays {contributionCount date}}}}}}""",
            "variables": {"userName": CONFIG['github_username']}
        }
        response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
        return response.json()

    def update_plot(self):
        contributions = self.fetch_contributions()
        weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

        weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
        contributions_grid = np.array(weeks_data).reshape((7, -1), order='F')

        # Calculate image dimensions
        img_height = contributions_grid.shape[0] * 3 + 2
        img_width = contributions_grid.shape[1] * 3 - 1
        img = np.full((img_height, img_width, 3), self.colors[0], dtype=np.uint8)  # Setting the default color

        for (i, j), usage in np.ndenumerate(contributions_grid):
            color_index = min(usage, len(self.colors) - 1)
            color = self.colors[color_index]
            img[i*3+1:i*3+3, j*3:j*3+2] = color

        # Convert numpy array to GdkPixbuf
        height, width, channels = img.shape
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(img.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * channels)

        # Set the pixbuf to the Gtk.Image
        self.image.set_from_pixbuf(pixbuf)

    def run(self):
        observer = Observer()
        event_handler = MyHandler(self)
        observer.schedule(event_handler, path=os.path.expanduser('~/.cache/wal'), recursive=False)
        observer.start()

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    contributionsWindow = GitHubContributionsWindow()
    contributionsWindow.run()

# LINE
# import os
# import gi
# gi.require_version('Gtk', '3.0')
# import numpy as np
# from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
# import requests
#
# CONFIG = {
#     'update_interval': 5000,
#     'github_username': 'laluxx',
#     'window_position_x': 850,
#     'window_position_y': 0,
#     'personal_access_token': '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'
# }
#
# class GitHubContributionsWindow(Gtk.Window):
#     def __init__(self):
#         super(GitHubContributionsWindow, self).__init__()
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(-1, 24)
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(CONFIG['window_position_x'], CONFIG['window_position_y'])
#
#         self.image = Gtk.Image()
#         self.add(self.image)
#
#         self.update_colors()
#
#     def hex_to_rgb(self, color):
#         color = color.lstrip('#')
#         return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
#
#     def update_colors(self):
#         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
#             color_lines = [line.strip() for line in f]
#             self.colors = [self.hex_to_rgb(color) for color in color_lines]
#
#         self.update_plot()
#
#     def fetch_contributions(self):
#         headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
#         json = {
#             "query": """query($userName:String!) {user(login: $userName){
#                        contributionsCollection {contributionCalendar {
#                        totalContributions weeks {contributionDays {contributionCount date}}}}}}""",
#             "variables": {"userName": CONFIG['github_username']}
#         }
#         response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
#         return response.json()
#
#     def update_plot(self):
#         contributions = self.fetch_contributions()
#         weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
#
#         weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
#         contributions_grid = np.array(weeks_data[::-1]).reshape((7, -1), order='F')
#
#         # Flip columns (horizontal flip)
#         contributions_grid = contributions_grid[:, ::-1]
#
#         # Flip rows (vertical flip)
#         contributions_grid = contributions_grid[::-1]
#
#         # Calculate image dimensions
#         img_height = contributions_grid.shape[0] * 3 + 2
#         img_width = contributions_grid.shape[1] * 3 - 1
#         img = np.full((img_height, img_width, 3), self.colors[0], dtype=np.uint8)  # Setting the default color
#
#         for (i, j), usage in np.ndenumerate(contributions_grid):
#             color_index = min(usage, len(self.colors) - 1)
#             color = self.colors[color_index]
#             img[i*3+1:i*3+3, j*3:j*3+2] = color
#
#         # Convert numpy array to GdkPixbuf
#         height, width, channels = img.shape
#         pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(img.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * channels)
#
#         # Set the pixbuf to the Gtk.Image
#         self.image.set_from_pixbuf(pixbuf)
#
#         # Refresh every 'update_interval' milliseconds
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
#
#     def run(self):
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()
#
# if __name__ == "__main__":
#     contributionsWindow = GitHubContributionsWindow()
#     contributionsWindow.run()





# IF THE WINDOW IS SMALL IT LOOKS BAD
# import os
# import gi
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from matplotlib.patches import Rectangle
# from gi.repository import Gtk, Gdk, GLib
# import requests
#
# CONFIG = {
#     'update_interval': 5000,
#     'github_username': 'laluxx',
#     'window_position_x': 850,
#     'window_position_y': 0,
#     'personal_access_token': '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'
# }
#
# class GitHubContributionsWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(-1, 24)  # Ensure the height of the window is set to 24 pixels.
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(CONFIG['window_position_x'], CONFIG['window_position_y'])
#
#         self.fig, self.ax = plt.subplots(figsize=(11,2.2))  # Graph's height is 22 pixels tall.
#         self.canvas = FigureCanvas(self.fig)
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
#     def fetch_contributions(self):
#         headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
#         json = {
#             "query" : "query($userName:String!) {user(login: $userName){contributionsCollection {contributionCalendar {totalContributions weeks {contributionDays {contributionCount date}}}}}}",
#             "variables": {"userName": CONFIG['github_username']}
#         }
#         response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
#         return response.json()
#
#     def update_plot(self):
#         self.ax.clear()
#
#         contributions = self.fetch_contributions()
#         weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
#         
#         weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
#         contributions_grid = np.array(weeks_data[::-1]).reshape((7, -1), order='F')
#         contributions_grid = contributions_grid[:, ::-1]
#
#         cell_size = 2
#         spacing = 1
#         total_size = cell_size + spacing
#
#         for (i, j), usage in np.ndenumerate(contributions_grid):
#             color_index = min(usage, len(self.colors) - 1)
#             color = self.colors[color_index]
#             rect_x = j * total_size
#             rect_y = i * total_size
#             rect = Rectangle((rect_x, rect_y), cell_size, cell_size, facecolor=color, edgecolor=None)
#             self.ax.add_patch(rect)
#
#         max_width = total_size * contributions_grid.shape[1]
#         max_height = total_size * 7
#         self.ax.set_xlim([0, max_width])
#         self.ax.set_ylim([0, max_height])
#         self.ax.set_aspect('equal', adjustable='box')
#         self.ax.axis('off')
#
#         self.canvas.draw_idle()
#
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
#
#     def run(self):
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()
#
# if __name__ == "__main__":
#     contributionsWindow = GitHubContributionsWindow()
#     contributionsWindow.run()









# NO GRID, CORRECT POSITION
# import os
# import gi
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from matplotlib.patches import Rectangle
# from gi.repository import Gtk, Gdk, GLib
# import requests
#
# CONFIG = {
#     'update_interval': 5000,
#     'github_username': 'laluxx',
#     'window_position_x': 850,
#     'window_position_y': 0,
#     'personal_access_token': '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'
# }
#
# class GitHubContributionsWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(-1, 24)  # Ensure the height of the window is set to 24 pixels.
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(CONFIG['window_position_x'], CONFIG['window_position_y'])
#
#         self.fig, self.ax = plt.subplots(figsize=(11,2.2))  # Graph's height is 22 pixels tall.
#         self.canvas = FigureCanvas(self.fig)
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
#     def fetch_contributions(self):
#         headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
#         json = {
#             "query" : "query($userName:String!) {user(login: $userName){contributionsCollection {contributionCalendar {totalContributions weeks {contributionDays {contributionCount date}}}}}}",
#             "variables": {"userName": CONFIG['github_username']}
#         }
#         response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
#         return response.json()
#
#     def update_plot(self):
#         self.ax.clear()
#
#         contributions = self.fetch_contributions()
#         weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
#         
#         weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
#         contributions_grid = np.array(weeks_data[::-1]).reshape((7, -1), order='F')
#         contributions_grid = contributions_grid[:, ::-1]
#
#         for (i, j), usage in np.ndenumerate(contributions_grid):
#             color_index = min(usage, len(self.colors) - 1)
#             color = self.colors[color_index]
#             rect = Rectangle((j, i), 1, 1, facecolor=color, edgecolor=None)  # Removed the edgecolor for the grid
#             self.ax.add_patch(rect)
#
#         self.ax.set_xlim([0, contributions_grid.shape[1]])
#         self.ax.set_ylim([0, 7])
#         self.ax.set_aspect('equal', adjustable='box')
#         self.ax.axis('off')
#
#         self.canvas.draw_idle()
#
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
#
#     def run(self):
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()
#
# if __name__ == "__main__":
#     contributionsWindow = GitHubContributionsWindow()
#     contributionsWindow.run()


# import os
# import gi
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from matplotlib.patches import Rectangle
# from gi.repository import Gtk, Gdk, GLib
# import requests
#
# CONFIG = {
#     'update_interval': 5000,  # Update interval for the plot in milliseconds
#     'github_username': 'laluxx',  # Replace with your GitHub username
#     'window_position_x': 850,  # Window x-position
#     'window_position_y': 0,  # Window y-position
#     'personal_access_token': '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'  # Replace with your personal access token
# }
#
# class GitHubContributionsWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(60, 24)
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(CONFIG['window_position_x'], CONFIG['window_position_y']) 
#
#         self.fig, self.ax = plt.subplots(figsize=(6,3), dpi=10)
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.set_size_request(60, 24)
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
#     def fetch_contributions(self):
#         headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
#         json = {
#             "query" : "query($userName:String!) {user(login: $userName){contributionsCollection {contributionCalendar {totalContributions weeks {contributionDays {contributionCount date}}}}}}",
#             "variables": {"userName": CONFIG['github_username']}
#         }
#         response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
#         return response.json()
#
#     def update_plot(self):
#         self.ax.clear()
#
#         contributions = self.fetch_contributions()
#         weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
#         
#         # Reshape the contributions data to be horizontal
#         weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
#         contributions_grid = np.array(weeks_data[::-1]).reshape((7, -1), order='F')
#         contributions_grid = contributions_grid[:, ::-1]
#
#         # Swap the roles of i and j in the loop
#         for (i, j), usage in np.ndenumerate(contributions_grid):
#             color_index = min(usage, len(self.colors) - 1)
#             color = self.colors[color_index]
#             rect = Rectangle((j, i), 1, 1, facecolor=color, edgecolor='white', linewidth=0.1)
#             self.ax.add_patch(rect)
#
#         self.ax.set_xlim([0, contributions_grid.shape[1]])
#         self.ax.set_ylim([0, 7])
#         self.ax.set_aspect('equal', adjustable='box')
#         self.ax.axis('off')
#
#         self.canvas.draw_idle()
#
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
#
#     def run(self):
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()
#
# if __name__ == "__main__":
#     contributionsWindow = GitHubContributionsWindow()
#     contributionsWindow.run()

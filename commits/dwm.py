#!/usr/bin/env python3
import os
import gi
import numpy as np
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

gi.require_version('Gtk', '3.0')

CONFIG = {
    'update_interval': 5000,
    'github_username': 'laluxx',
    'window_position_x': 950,
    'window_position_y': 0,
    'personal_access_token': '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'
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
        self.label = Gtk.Label()
        self.label.set_visible(False)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(self.image, True, True, 0)
        self.box.pack_start(self.label, True, True, 0)

        self.add(self.box)
        self.update_colors()

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press_event)

    def on_button_press_event(self, widget, event):
        self.label.set_visible(not self.label.get_visible())

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color) for color in color_lines]

        rgba = Gdk.RGBA(*[c / 255.0 for c in self.colors[0]], 1.0)
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
        response_json = response.json()
        if 'data' not in response_json:
            print("Unexpected response from GitHub API:")
            print(response_json)
        return response_json

    def update_plot(self):
        contributions = self.fetch_contributions()
        total_contributions = contributions['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
        self.label.set_text(f"Total Contributions: {total_contributions}")

        weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
        expected_size = 7 * len(weeks)
        while len(weeks_data) < expected_size:
            weeks_data.append(0)

        contributions_grid = np.array(weeks_data).reshape((7, -1), order='F')

        img_height = contributions_grid.shape[0] * 3 + 2
        img_width = contributions_grid.shape[1] * 3 - 1
        img = np.full((img_height, img_width, 3), self.colors[0], dtype=np.uint8)

        for (i, j), usage in np.ndenumerate(contributions_grid):
            color_index = min(usage, len(self.colors) - 1)
            color = self.colors[color_index]
            img[i * 3 + 1:i * 3 + 3, j * 3:j * 3 + 2] = color

        height, width, channels = img.shape
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(img.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8,
                                                 width, height, width * channels)
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









# #!/usr/bin/env python3
# import os
# import gi
# gi.require_version('Gtk', '3.0')
# import numpy as np
# from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
# import requests
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
#
# CONFIG = {
#     'update_interval': 5000,
#     'github_username': 'laluxx',
#     'window_position_x': 950,
#     'window_position_y': 0,
#     'personal_access_token': 'YourTokenHere',  # Replace with your personal access token
#     'transparent': True,  # Set to False for original color scheme
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
# class GitHubContributionsWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
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
#         if CONFIG['transparent']:
#             rgba = Gdk.RGBA(0, 0, 0, 0)  # Fully Transparent
#         else:
#             rgba = Gdk.RGBA(*[c/255.0 for c in self.colors[0]], 1.0)
#         
#         self.override_background_color(Gtk.StateFlags.NORMAL, rgba)
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
#         
#         if response.ok:
#             return response.json()
#         
#         print(f"Failed to fetch contributions. Response: {response.text}")
#         return None
#
#     def update_plot(self):
#         contributions_json = self.fetch_contributions()
#         if not contributions_json:
#             return
#         
#         weeks = contributions_json['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
#         # Continue with the existing logic to plot contributions...
#
#     def run(self):
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
#     contributionsWindow = GitHubContributionsWindow()
#     contributionsWindow.run()
#
#
#
#
#
#
# # #!/usr/bin/env python3
# #
# # # NEW WEEK FIX
# # import os
# # import gi
# # gi.require_version('Gtk', '3.0')
# # import numpy as np
# # from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
# # import requests
# # from watchdog.observers import Observer
# # from watchdog.events import FileSystemEventHandler
# #
# # CONFIG = {
# #     'update_interval': 5000,
# #     'github_username': 'laluxx',
# #     'window_position_x': 950,
# #     'window_position_y': 0,
# #     'personal_access_token': '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'
# # }
# #
# # class MyHandler(FileSystemEventHandler):
# #     def __init__(self, overlay):
# #         self.overlay = overlay
# #
# #     def on_modified(self, event):
# #         if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
# #             GLib.idle_add(self.overlay.update_colors)
# #
# # class GitHubContributionsWindow(Gtk.Window):
# #     def __init__(self):
# #         super(GitHubContributionsWindow, self).__init__()
# #
# #         self.set_keep_above(True)
# #         self.set_decorated(False)
# #         self.set_default_size(-1, 24)
# #         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
# #         self.move(CONFIG['window_position_x'], CONFIG['window_position_y'])
# #
# #         self.image = Gtk.Image()
# #         self.add(self.image)
# #
# #         self.update_colors()
# #
# #     def hex_to_rgb(self, color):
# #         color = color.lstrip('#')
# #         return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
# #
# #     def update_colors(self):
# #         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
# #             color_lines = [line.strip() for line in f]
# #             self.colors = [self.hex_to_rgb(color) for color in color_lines]
# #
# #         rgba = Gdk.RGBA(*[c/255.0 for c in self.colors[0]], 1.0)
# #         self.override_background_color(Gtk.StateFlags.NORMAL, rgba)
# #
# #         self.update_plot()
# #
# #     def fetch_contributions(self):
# #         headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
# #         json = {
# #             "query": """query($userName:String!) {user(login: $userName){
# #                        contributionsCollection {contributionCalendar {
# #                        totalContributions weeks {contributionDays {contributionCount date}}}}}}""",
# #             "variables": {"userName": CONFIG['github_username']}
# #         }
# #         response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
# #         response_json = response.json()
# #
# #         # Print the response if there's no 'data' key
# #         if 'data' not in response_json:
# #             print("Unexpected response from GitHub API:")
# #             print(response_json)
# #
# #         return response_json
# #
# #     def update_plot(self):
# #         contributions = self.fetch_contributions()
# #         weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
# #
# #         weeks_data = [day['contributionCount'] for week in weeks for day in week['contributionDays']]
# #         
# #         # Calculate the expected size
# #         expected_size = 7 * len(weeks)
# #
# #         # If the fetched data doesn't align with the expected size, pad with zeros
# #         while len(weeks_data) < expected_size:
# #             weeks_data.append(0)
# #
# #         contributions_grid = np.array(weeks_data).reshape((7, -1), order='F')
# #
# #         # Calculate image dimensions
# #         img_height = contributions_grid.shape[0] * 3 + 2
# #         img_width = contributions_grid.shape[1] * 3 - 1
# #         img = np.full((img_height, img_width, 3), self.colors[0], dtype=np.uint8)  # Setting the default color
# #
# #         for (i, j), usage in np.ndenumerate(contributions_grid):
# #             color_index = min(usage, len(self.colors) - 1)
# #             color = self.colors[color_index]
# #             img[i*3+1:i*3+3, j*3:j*3+2] = color
# #
# #         # Convert numpy array to GdkPixbuf
# #         height, width, channels = img.shape
# #         pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(img.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * channels)
# #
# #         # Set the pixbuf to the Gtk.Image
# #         self.image.set_from_pixbuf(pixbuf)
# #
# #
# #     def run(self):
# #         observer = Observer()
# #         event_handler = MyHandler(self)
# #         observer.schedule(event_handler, path=os.path.expanduser('~/.cache/wal'), recursive=False)
# #         observer.start()
# #
# #         self.connect("destroy", Gtk.main_quit)
# #         self.show_all()
# #         Gtk.main()
# #
# # if __name__ == "__main__":
# #     contributionsWindow = GitHubContributionsWindow()
# #     contributionsWindow.run()

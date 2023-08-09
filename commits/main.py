#!/usr/bin/env python3



import os
import gi
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.patches import Rectangle
from gi.repository import Gtk, Gdk, GLib
import requests

CONFIG = {
    'update_interval': 5000,  # Update interval for the plot in milliseconds
    'github_username': 'laluxx',  # Replace with your GitHub username
    'window_position_x': 850,  # Window x-position
    'window_position_y': 0,  # Window y-position
    'personal_access_token': 'your_personal_access_token'  # Replace with your personal access token
}

class GitHubContributionsWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(60, 24)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(CONFIG['window_position_x'], CONFIG['window_position_y']) 

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

    def fetch_contributions(self):
        headers = {"Authorization": f"Bearer {CONFIG['personal_access_token']}"}
        json = {
            "query" : "query($userName:String!) {user(login: $userName){contributionsCollection {contributionCalendar {totalContributions weeks {contributionDays {contributionCount date}}}}}}",
            "variables": {"userName": CONFIG['github_username']}
        }
        response = requests.post('https://api.github.com/graphql', json=json, headers=headers)
        return response.json()

    def update_plot(self):
        self.ax.clear()

        contributions = self.fetch_contributions()
        weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        contributions_grid = np.array([day['contributionCount'] for week in weeks for day in week['contributionDays']]).reshape((-1, 7))

        for (j, i), usage in np.ndenumerate(contributions_grid):
            color_index = min(usage, len(self.colors) - 1)
            color = self.colors[color_index]
            rect = Rectangle((i, j), 1, 1, facecolor=color, edgecolor='white', linewidth=0.1)
            self.ax.add_patch(rect)

        self.ax.set_xlim([0, 7])
        self.ax.set_ylim([0, len(contributions_grid)])
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.axis('off')

        self.canvas.draw_idle()

        GLib.timeout_add(CONFIG['update_interval'], self.update_plot)

    def run(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    contributionsWindow = GitHubContributionsWindow()
    contributionsWindow.run()

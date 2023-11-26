#!/usr/bin/env python3

import gi
import os
import subprocess
import numpy as np

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

class ToggleButtonWindow(Gtk.Window):
    def __init__(self):
        super(ToggleButtonWindow, self).__init__()

        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(40, 40)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.button = Gtk.EventBox()
        self.button.connect("button-press-event", self.on_button_press)
        self.add(self.button)

        self.image = Gtk.Image()
        self.button.add(self.image)
        self.update_colors()
        self.render_button_normal()

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color) for color in color_lines]

    def render_button_normal(self):
        # Implement your normal button appearance using the colors from wal
        height, width = 40, 40
        img = np.full((height, width, 3), self.colors[6], dtype=np.uint8)
        self._set_image_from_np_array(img)

    def render_button_pressed(self):
        # Implement the pressed button appearance using the colors from wal
        height, width = 40, 40
        img = np.full((height, width, 3), self.colors[0], dtype=np.uint8)
        img[0:5, :] = self.colors[1]
        img[-5:, :] = self.colors[1]
        self._set_image_from_np_array(img)

    def _set_image_from_np_array(self, img):
        height, width, channels = img.shape
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(img.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * channels)
        self.image.set_from_pixbuf(pixbuf)

    def on_button_press(self, widget, event):
        process_name = "blur-my-wallpaper"
        try:
            # This will get the list of all processes running with the name 'blur-my-wallpaper'
            output = subprocess.check_output(['pgrep', '-f', process_name]).decode('utf-8')
            if output:  # If there's an output, it means the process is running
                subprocess.run(['pkill', '-f', process_name])
                self.render_button_pressed()
            else:  # If there's no output, it means the process is not running
                subprocess.run([process_name])
                self.render_button_normal()
        except subprocess.CalledProcessError:  # pgrep will throw an error if it doesn't find the process. So, we start it in that case
            subprocess.run([process_name])
            self.render_button_normal()

    def run(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()


if __name__ == "__main__":
    toggleButton = ToggleButtonWindow()
    toggleButton.run()



# V1
# import gi
# import os
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk, Gdk
#
# CONFIG = {
#     'color_index': 3,
#     'wal_colors_path': os.path.expanduser('~/.cache/wal/colors')
# }
#
# class ToggleButtonWindow(Gtk.Window):
#
#     def __init__(self):
#         super().__init__()
#
#         # Adjust window properties to match the NetworkStatWindow example
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(100, 50)
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         # Set desired position using the move method
#         #self.move(desired_x_position, desired_y_position)
#         self.move(426, 0)  # Sample position
#
#         self.button = Gtk.Button(label="Toggle")
#         self.button.connect("clicked", self.on_button_click)
#         self.button.set_can_focus(False)
#         
#         self.add(self.button)
#         
#         self.set_button_color()
#         self.is_blurred = False
#
#     def on_button_click(self, button):
#         if not self.is_blurred:
#             os.system('blur-my-wallpaper')
#             self.is_blurred = True
#         else:
#             os.system('pkill blur-my-wallpap')
#             self.is_blurred = False
#
#     def set_button_color(self):
#         with open(CONFIG['wal_colors_path'], 'r') as f:
#             colors = [line.strip() for line in f]
#             button_color = colors[CONFIG['color_index']]
#
#         css_string = f"""
#         button {{
#             background-color: {button_color};
#             border: none;
#         }}
#         """
#
#         css_provider = Gtk.CssProvider()
#         css_provider.load_from_data(css_string.encode())
#
#         Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
#
# if __name__ == "__main__":
#     win = ToggleButtonWindow()
#     win.connect("destroy", Gtk.main_quit)
#     win.show_all()
#     Gtk.main()



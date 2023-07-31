# THEME BAR
# TODO: be on top of only xmobar not all windows
# DOUBLE SMOOTH
# ONLY MIC AUDIO FOR NOW
import os
import numpy as np
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from gi.repository import Gtk, Gdk, GLib
import sounddevice as sd
from scipy.fftpack import fft
import collections

# Configuration parameters
CONFIG = {
    'fft_size': 1024, # FFT size
    'buffer_size': 44100, # Audio buffer size
    'audio_rate': 44100, # Audio sample rate
    'update_interval': 10, # Update interval for the plot in milliseconds
    'smoothing_factor': 0.2, # Smoothing factor for moving average
    'noise_threshold': 0.01, # Noise threshold for noise gate
    'color_indices': [0, 3, 6, 9], # Indices of colors to use from the wal cache
    'device_index': None, # Index of the audio device to use. If None, the default device is used
    'num_bars': 50, # Number of bars in the visualizer
    'bar_width': 0.8, # Width of the bars in the visualizer
    'bar_gap': 0.2 # Gap between the bars in the visualizer
}

class MyHandler(FileSystemEventHandler):
    def __init__(self, overlay):
        self.overlay = overlay

    def on_modified(self, event):
        if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
            GLib.idle_add(self.overlay.update_colors)

class OverlayWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.colors = []
        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=CONFIG['audio_rate'], device=CONFIG['device_index'])
        self.stream.start()
        self.audio_buffer = collections.deque([0]*CONFIG['buffer_size'], maxlen=CONFIG['buffer_size'])
        self.prev_spectrum = None

        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_default_size(474, 23)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.move(426, 0)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(474, 23)

        self.add(self.canvas)

        self.update_colors()
        self.update_plot()

    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))

    def update_colors(self):
        with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
            color_lines = [line.strip() for line in f]
            self.colors = [self.hex_to_rgb(color_lines[i]) for i in CONFIG['color_indices']]

        if self.colors:
            self.fig.patch.set_facecolor(self.colors[0])

    def audio_callback(self, indata, frames, time, status):
        self.audio_buffer.extend(indata[:, 0])

    def update_plot(self):
        self.ax.clear()

        # Perform FFT on audio data
        yf = fft(list(self.audio_buffer)[-CONFIG['fft_size']:])
        spectrum = np.abs(yf[:CONFIG['fft_size']//2])

        # Apply moving average filter
        if self.prev_spectrum is not None:
            spectrum = CONFIG['smoothing_factor']*spectrum + (1-CONFIG['smoothing_factor'])*self.prev_spectrum

        # Apply noise gate
        spectrum[spectrum < CONFIG['noise_threshold']] = 0

        self.prev_spectrum = spectrum

        # Draw bars
        color = self.colors[1] if len(self.colors) > 1 else 'b'
        self.ax.bar(np.arange(CONFIG['num_bars']), spectrum[:CONFIG['num_bars']], color=color, width=CONFIG['bar_width'])

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
    overlay = OverlayWindow()
    overlay.run()




# THEME 2
# ONLYMIC
# SMOOTH
# import os
# import numpy as np
# import matplotlib.pyplot as plt
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from gi.repository import Gtk, Gdk, GLib
# import sounddevice as sd
# from scipy.fftpack import fft
# import collections
#
# # Configuration parameters
# CONFIG = {
#     'fft_size': 1024, # FFT size
#     'buffer_size': 44100, # Audio buffer size
#     'audio_rate': 44100, # Audio sample rate
#     'update_interval': 10, # Update interval for the plot in milliseconds
#     'smoothing_factor': 0.2, # Smoothing factor for moving average
#     'color_indices': [0, 3, 6, 9] # Indices of colors to use from the wal cache
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
# class OverlayWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.colors = []
#         self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=CONFIG['audio_rate'])
#         self.stream.start()
#         self.audio_buffer = collections.deque([0]*CONFIG['buffer_size'], maxlen=CONFIG['buffer_size'])
#         self.fft_buffer = np.zeros(CONFIG['fft_size'])
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(474, 23)
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(426, 0)
#
#         self.fig, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.set_size_request(474, 23)
#
#         self.add(self.canvas)
#
#         self.update_colors()
#         self.update_plot()
#
#     def hex_to_rgb(self, color):
#         color = color.lstrip('#')
#         return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))
#
#     def update_colors(self):
#         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
#             color_lines = [line.strip() for line in f]
#             self.colors = [self.hex_to_rgb(color_lines[i]) for i in CONFIG['color_indices']]
#
#         if self.colors:
#             self.fig.patch.set_facecolor(self.colors[0])
#
#     def audio_callback(self, indata, frames, time, status):
#         self.audio_buffer.extend(indata[:, 0])
#
#     def update_plot(self):
#         self.ax.clear()
#
#         # Perform FFT on audio data
#         yf = fft(list(self.audio_buffer)[-CONFIG['fft_size']:])
#         yf_smooth = CONFIG['smoothing_factor'] * np.abs(yf) + (1 - CONFIG['smoothing_factor']) * self.fft_buffer
#         self.fft_buffer = yf_smooth
#
#         N = CONFIG['fft_size']
#         T = 1.0 / CONFIG['audio_rate']
#         xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
#
#         # Generate a waveform plot
#         color = self.colors[1] if len(self.colors) > 1 else 'b'
#         self.ax.fill_between(xf, 20 * np.log10(yf_smooth[:N//2]), color=color, alpha=0.7)
#
#         self.ax.set_facecolor(self.colors[0])
#         self.ax.axis('off')
#
#         self.canvas.draw_idle()
#
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
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
#     overlay = OverlayWindow()
#     overlay.run()




# THEME 1
# SMOOTH
# import os
# import numpy as np
# import matplotlib.pyplot as plt
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from gi.repository import Gtk, Gdk, GLib
# import sounddevice as sd
# from scipy.fftpack import fft
# import collections
#
# # Configuration parameters
# CONFIG = {
#     'fft_size': 1024, # FFT size
#     'buffer_size': 44100, # Audio buffer size
#     'audio_rate': 44100, # Audio sample rate
#     'update_interval': 10, # Update interval for the plot in milliseconds
#     'smoothing_factor': 0.2, # Smoothing factor for moving average
#     'color_indices': [0, 3, 6, 9] # Indices of colors to use from the wal cache
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
# class OverlayWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.colors = []
#         self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=CONFIG['audio_rate'])
#         self.stream.start()
#         self.audio_buffer = collections.deque([0]*CONFIG['buffer_size'], maxlen=CONFIG['buffer_size'])
#         self.fft_buffer = np.zeros(CONFIG['fft_size'])
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(474, 23)
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(426, 0)
#
#         self.fig, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.set_size_request(474, 23)
#
#         self.add(self.canvas)
#
#         self.update_colors()
#         self.update_plot()
#
#     def hex_to_rgb(self, color):
#         color = color.lstrip('#')
#         return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))
#
#     def update_colors(self):
#         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
#             color_lines = [line.strip() for line in f]
#             self.colors = [self.hex_to_rgb(color_lines[i]) for i in CONFIG['color_indices']]
#
#         if self.colors:
#             self.fig.patch.set_facecolor(self.colors[0])
#
#     def audio_callback(self, indata, frames, time, status):
#         self.audio_buffer.extend(indata[:, 0])
#
#     def update_plot(self):
#         self.ax.clear()
#
#         # Perform FFT on audio data
#         yf = fft(list(self.audio_buffer)[-CONFIG['fft_size']:])
#         yf_smooth = CONFIG['smoothing_factor'] * np.abs(yf) + (1 - CONFIG['smoothing_factor']) * self.fft_buffer
#         self.fft_buffer = yf_smooth
#
#         N = CONFIG['fft_size']
#         T = 1.0 / CONFIG['audio_rate']
#         xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
#         color = self.colors[1] if len(self.colors) > 1 else 'b'
#         self.ax.semilogx(xf, 20 * np.log10(yf_smooth[:N//2]), color=color)
#
#         self.ax.set_facecolor(self.colors[0])
#         self.ax.axis('off')
#
#         self.canvas.draw_idle()
#
#         GLib.timeout_add(CONFIG['update_interval'], self.update_plot)
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
#     overlay = OverlayWindow()
#     overlay.run()






# ORIGINAL
# SIMULATING GOOD
# CHANGE COLORS ONE THE FLY [x]
# import gi
# import os
# import numpy as np
# import matplotlib.pyplot as plt
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
# from gi.repository import Gtk, Gdk, GLib
#
# class MyHandler(FileSystemEventHandler):
#     def __init__(self, overlay):
#         self.overlay = overlay
#
#     def on_modified(self, event):
#         if event.src_path == os.path.expanduser('~/.cache/wal/colors'):
#             GLib.idle_add(self.overlay.update_colors)
#
# class OverlayWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()
#
#         self.colors = []
#
#         self.set_keep_above(True)
#         self.set_decorated(False)
#         self.set_default_size(474, 23)
#         self.set_type_hint(Gdk.WindowTypeHint.DOCK)
#         self.move(426, 0)
#
#         self.fig, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.set_size_request(474, 23)
#
#         self.add(self.canvas)
#
#         self.update_colors()
#         self.update_plot()
#
#     def hex_to_rgb(self, color):
#         color = color.lstrip('#')
#         return tuple(int(color[i:i+2], 16) / 255 for i in (0, 2 ,4))
#
#     def update_colors(self):
#         with open(os.path.expanduser('~/.cache/wal/colors'), 'r') as f:
#             self.colors = [self.hex_to_rgb(line.strip()) for line in f]
#
#         if self.colors:
#             self.fig.patch.set_facecolor(self.colors[0])
#
#     def update_plot(self):
#         self.ax.clear()
#
#         data = np.random.rand(50)
#         if self.colors and len(self.colors) > 3:
#             self.ax.plot(data, color=self.colors[3])
#         else:
#             self.ax.plot(data)
#
#         self.ax.set_facecolor(self.colors[0])
#         self.ax.axis('off')
#
#         self.canvas.draw_idle()
#
#         GLib.timeout_add(1000, self.update_plot)
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
#     overlay = OverlayWindow()
#     overlay.run()

import threading
import logging
import random
from ctypes import windll
import time
from datetime import datetime
import win32gui, win32ui, win32con
from PIL import Image

class ScreenReaderAsync(threading.Thread):
    """Class reading RGB values from the screen in a separate thread.
    Using the code from 
    https://stackoverflow.com/questions/48092655/memory-leak-with-createdcfromhandle-createcompatibledc

    Args:
        name (str): name of the thread
        index_range (list): range of LED indices to read data from
        queue (queue.Queue): queue to add the values to
        led_map (list): LED index to pixel coordinates mapping from the profile
    
    Attributes:
        name (str): name of the thread
        dc (str): hdc screen object
        index_range (list): range of LED indices to read data from
        queue (queue.Queue): queue to add the values to
        led_map (list): LED index to pixel coordinates mapping from the profile
        index_order (list): list of indices in the index_range in a random order
        logger (Logger): logger object used to write logs from this thread
    """
    def __init__(self, settings, name=None, index_range=[], queue=None):
        super(ScreenReaderAsync, self).__init__()
        self.name = name
        self.dc = windll.user32.GetDC(None)
        self.index_range = index_range
        self.queue = queue
        self.settings = settings
        self.logger = logging.getLogger(self.name)
        self.setup()
    
    def setup(self):
        """Set up variables for the run.
        """
        self.frame_min_duration = 1.0 / self.settings.fps_limit  # seconds
        self.index_order = list(range(self.index_range[0], self.index_range[1]))
        random.shuffle(self.index_order)

        # get a bbox
        led_coord_lists = [self.settings.get_pixel_list(i) for i in self.index_order]
        max_x = max(coord[0] for led_pixels in led_coord_lists for coord in led_pixels)
        min_x = min(coord[0] for led_pixels in led_coord_lists for coord in led_pixels)
        max_y = max(coord[1] for led_pixels in led_coord_lists for coord in led_pixels)
        min_y = min(coord[1] for led_pixels in led_coord_lists for coord in led_pixels)
        self.bbox = (min_x, min_y, max_x+1, max_y+1)

        # set up some helpful variables
        self.size = (self.bbox[2]-self.bbox[0], self.bbox[3]-self.bbox[1])
        self.position = (self.bbox[0], self.bbox[1])
        self.hwnd = None

    def run(self):
        """Run the loop of reading the pixel values and adding them to the queue.
        """
        self.logger.info("Started screen reader")

        while True:
            # start a frame
            frame_start = datetime.utcnow()

            try:
                # get a screenshot using BitBlt
                hdc = win32gui.GetWindowDC(self.hwnd)
                dc = win32ui.CreateDCFromHandle(hdc)
                memdc = dc.CreateCompatibleDC()
                bitmap = win32ui.CreateBitmap()
                bitmap.CreateCompatibleBitmap(dc, self.size[0], self.size[1])
                memdc.SelectObject(bitmap)
                memdc.BitBlt((0, 0), self.size, dc, self.position, win32con.SRCCOPY)
                bits = bitmap.GetBitmapBits(True)
                current_screenshot = Image.frombuffer('RGB', self.size, bits, 'raw', 'BGRX', 0, 1)
            except Exception as e:
                self.logger.error(f"Error getting a screenshot in ScreenReaderAsync.run(): {e}")
                time.sleep(1)
                continue
            finally:
                win32gui.DeleteObject(bitmap.GetHandle())
                memdc.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, hdc)

            # add the pixel values to a queue
            for i in self.index_order:
                item = self._mean_rgb([
                    current_screenshot.getpixel((coords[0]-self.bbox[0], coords[1]-self.bbox[1]))
                    for coords in self.settings.get_pixel_list(i)
                ])
                if item is not None:
                    self.queue.put(i, item)
            
            # how long was this frame in milliseconds
            frame_duration = (datetime.utcnow() - frame_start).total_seconds()
            if frame_duration < 1e-5: frame_duration
            time_left_in_frame = self.frame_min_duration - frame_duration
            # make sure it waits for at least a millisecond
            # this miraculously saves some CPU usage
            if time_left_in_frame <= 0:
                time_left_in_frame = 1e-3
            # wait until the next frame
            self.logger.debug(f"Frame ended, frame={frame_duration*1000:2f}ms, " +
                              f"capped_at={self.settings.fps_limit}fps/{1.0/self.settings.fps_limit}s, " +
                              f"wait={time_left_in_frame}")
            time.sleep(time_left_in_frame)

    def _mean_rgb(self, rgb_values):
        """Calculate a mean value of an array of RGB values.

        Args:
            rgb_values (list): list of RGB tuples (0..255)

        Returns:
            tuple: 3 RGB values
        """
        N = len(rgb_values)
        if N == 1:
            return rgb_values[0]
        return (
            sum(value[0] for value in rgb_values) // N,
            sum(value[1] for value in rgb_values) // N,
            sum(value[2] for value in rgb_values) // N,
        )

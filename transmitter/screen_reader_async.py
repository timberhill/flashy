import threading
import logging
import random
import time
from datetime import datetime
from sys import platform

if platform == "darwin":
    from .cg_screenshot import CGScreenshot as Screenshot
elif platform == "win32":
    from .bitblt_screenshot import BitBltScreenshot as Screenshot
elif platform == "linux" or platform == "linux2":
    raise NotImplementedError("Looks like you're trying to run this in linux, but flashy only works on windows and macos for now.")


class ScreenReaderAsync(threading.Thread):
    """Class reading RGB values from the screen in a separate thread.
    Using the code from 
    https://stackoverflow.com/questions/48092655/memory-leak-with-createdcfromhandle-createcompatibledc

    Args:
        settings (settings.Settings): flashy settings object
        name (str): name of the thread
        index_range (list): range of LED indices to read data from
        queue (queue.Queue): queue to add the values to
    
    Attributes:
        settings (settings.Settings): flashy settings object
        name (str): name of the thread
        index_range (list): range of LED indices to read data from
        queue (queue.Queue): queue to add the values to
        index_order (list): list of indices in the index_range in a random order
        logger (Logger): logger object used to write logs from this thread
    """
    def __init__(self, settings, name=None, index_range=[], queue=None):
        super(ScreenReaderAsync, self).__init__()
        self.name = name
        self.index_range = index_range
        self.queue = queue
        self.settings = settings
        self.logger = logging.getLogger(self.name)
        self.setup()
    
    def setup(self):
        """Set up variables for the run.
        """
        self._frame_min_duration = 1.0 / self.settings.fps_limit  # seconds
        self.index_order = list(range(self.index_range[0], self.index_range[1]))
        random.shuffle(self.index_order)

        # get a bbox
        led_coord_lists = [self.settings.get_pixel_list(i) for i in self.index_order]
        max_x = max(coord[0] for led_pixels in led_coord_lists for coord in led_pixels)
        min_x = min(coord[0] for led_pixels in led_coord_lists for coord in led_pixels)
        max_y = max(coord[1] for led_pixels in led_coord_lists for coord in led_pixels)
        min_y = min(coord[1] for led_pixels in led_coord_lists for coord in led_pixels)
        self._bbox = (min_x, min_y, max_x+1, max_y+1)

        # set up some helpful variables
        self.hwnd = None

    def _process_frame(self):
        with Screenshot(bbox=self._bbox) as screenshot:
            # add the pixel values to a queue
            for i in self.index_order:
                item = self._mean_rgb([
                    screenshot.getpixel(coords[0]-self._bbox[0], coords[1]-self._bbox[1])
                    for coords in self.settings.get_pixel_list(i)
                ])
                if item is not None:
                    self.queue.put(i, item)


    def run(self):
        """Run the loop of reading the pixel values and adding them to the queue.
        """
        self.logger.debug("Started screen reader")

        while True:
            if self.queue.full():
                # if the queue is full, wait this one out
                time.sleep(1.0/self.settings.fps_limit)
                continue
                
            # start a frame
            frame_start = datetime.utcnow()

            # get the screenshot and add it to the queue
            self._process_frame()
        
            # how long was this frame in milliseconds
            frame_duration = (datetime.utcnow() - frame_start).total_seconds()
            time_left_in_frame = self._frame_min_duration - frame_duration

            # make sure it waits for at least a millisecond
            # (this miraculously saves some CPU usage)
            if time_left_in_frame <= 0:
                time_left_in_frame = 1e-3

            # wait until the next frame
            self.logger.debug(f"Frame ended, duration={frame_duration*1000:1f}ms, " +
                              f"capped_at={self.settings.fps_limit}fps/{1000/self.settings.fps_limit:1f}ms, " +
                              f"wait={time_left_in_frame*1000:.1f}ms")
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

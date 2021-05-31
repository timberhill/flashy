import threading
import logging
import random
from ctypes import windll


class ScreenReaderAsync(threading.Thread):
    """Class reading RGB values from the screen in a separate thread.

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
    def __init__(self, name=None, index_range=[], queue=None, led_map=[]):
        super(ScreenReaderAsync, self).__init__()
        self.name = name
        self.dc = windll.user32.GetDC(None)
        self.index_range = index_range
        self.queue = queue
        self.led_map = led_map
        self.index_order = list(range(self.index_range[0], self.index_range[1]))
        random.shuffle(self.index_order)
        self.logger = logging.getLogger(self.name)

    def run(self):
        """Run the loop of reading the pixel values and adding them to the queue.
        """
        self.logger.info("Started screen reader")
        while True:
            for i in self.index_order:
                item = self.get_pixel(self.led_map[i])
                if item is not None:
                    self.queue.put(i, item)
        
    def get_pixel(self, coords):
        """Get RGB of a pixel on a screen.

        Args:
            coords (list): coordinates of the pixel on a screen

        Returns:
            tuple with 3 values of red, green, and blue, OR None if there is no value to be read at these coordinates.
        """
        colorref = windll.gdi32.GetPixel(self.dc, *coords)

        if colorref < 0:
            self.logger.debug(f"Got pixel value with negative COLORREF, coords={coords} COLORREF={colorref}")
            return None
        
        rgb = tuple(int.to_bytes(
            colorref,
            length=3,
            byteorder="little"
        ))

        self.logger.debug(f"Got pixel value, coords={coords} COLORREF={colorref} rgb={rgb}")
        return rgb

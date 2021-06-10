import threading
import logging
import random
from ctypes import windll
import time

# pip install pywin32
import win32gui, win32ui, win32con
from PIL import Image

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
    def __init__(self, settings, name=None, index_range=[], queue=None):
        super(ScreenReaderAsync, self).__init__()
        self.name = name
        self.dc = windll.user32.GetDC(None)
        self.index_range = index_range
        self.queue = queue
        self.settings = settings
        self.index_order = list(range(self.index_range[0], self.index_range[1]))
        random.shuffle(self.index_order)
        self.logger = logging.getLogger(self.name)

    def run(self):
        """Run the loop of reading the pixel values and adding them to the queue.
        """
        self.logger.info("Started screen reader")
        
        #win32gui.ReleaseDC(hwnd, hDC)
        from datetime import datetime
        led_coord_lists = [(i, self.settings.get_pixel_list(i)) for i in self.index_order]
        max_x = max(coord[0] for led_pixels in led_coord_lists for coord in led_pixels[1])
        min_x = min(coord[0] for led_pixels in led_coord_lists for coord in led_pixels[1])
        max_y = max(coord[1] for led_pixels in led_coord_lists for coord in led_pixels[1])
        min_y = min(coord[1] for led_pixels in led_coord_lists for coord in led_pixels[1])
        bbox = (min_x, min_y, max_x+1, max_y+1)
        print(bbox)

        
        self.size = (bbox[2]-bbox[0], bbox[3]-bbox[1])
        self.position = (bbox[0], bbox[1])
        hwnd = None
        hDC = win32gui.GetWindowDC(hwnd)
        self.windowDC = win32ui.CreateDCFromHandle(hDC)
        self.newDC = self.windowDC.CreateCompatibleDC()


        ranges = [1e10, 0.001, 1e10, 0.001]
        while True:
            time.sleep(float(self.settings.frame_delay)/1000)
            start = datetime.now()



            self.bitmap = win32ui.CreateBitmap()
            self.bitmap.CreateCompatibleBitmap(self.windowDC, self.size[0], self.size[1])
            self.newDC.SelectObject(self.bitmap)
            self.newDC.BitBlt((0, 0), self.size, self.windowDC, self.position, win32con.SRCCOPY)
            # bmpinfo = self.bitmap.GetInfo()
            bmpstr  = self.bitmap.GetBitmapBits(True)
            self.current_screenshot = Image.frombuffer('RGB', self.size, bmpstr, 'raw', 'BGRX', 0, 1)




            for i in self.index_order:
                item = self._mean_rgb([
                    self.current_screenshot.getpixel((coords[0]-bbox[0], coords[1]-bbox[1]))
                    for coords in self.settings.get_pixel_list(i)
                ])
                if item is not None:
                    self.queue.put(i, item)

            grabtime = (datetime.now() - start).total_seconds()*1000
            perpixel = grabtime/self.settings.strip_size
            if grabtime <= 0.001:
                grabtime = 1
            if perpixel <= 0.001:
                perpixel = 1
            ranges = [
                grabtime if (grabtime < ranges[0]) else ranges[0],
                grabtime if grabtime > ranges[1] else ranges[1],
                perpixel if perpixel < ranges[2] else ranges[2],
                perpixel if perpixel > ranges[3] else ranges[3],
            ]
            # self.logger.info(f"grabtime: {grabtime}, perpixel: {perpixel}, ranges: {ranges}, fpss: {[1000.0/x if x > 0 else '000' for x in ranges]}")
        
    def get_pixel(self, x, y):
        """Get RGB of a pixel on a screen.

        Args:
            coords (list): coordinates of the pixel on a screen (x, y)

        Returns:
            tuple with 3 values of red, green, and blue, OR None if there is no value to be read at these coordinates.
        """
        colorref = windll.gdi32.GetPixel(self.dc, x, y)

        if colorref < 0:
            self.logger.debug(f"Got pixel value with negative COLORREF, coords=[{x},{y}] COLORREF={colorref}")
            return None
        
        rgb = tuple(int.to_bytes(
            colorref,
            length=3,
            byteorder="little"
        ))

        self.logger.debug(f"Got pixel value, coords=[{x},{y}] COLORREF={colorref} rgb={rgb}")
        return rgb
    
    def get_area(self, bbox):
        """Get an average RGB of pixels on the screen.

        Args:
            bbox (list): coordinates of the upper-left and lower-right corners on a box on a screen

        Returns:
            tuple with 3 values of red, green, and blue, OR None if there is no value to be read at these coordinates.
        """
        pixel_values = [
            self.get_pixel(x, y)
            for x in range(bbox[0], bbox[2])
            for y in range(bbox[1], bbox[3])
        ]

        mean_value = self._mean_rgb(pixel_values)

        self.logger.debug(f"Got pixel area, bbox=[{bbox}] arr={pixel_values} mean={mean_value}")
        return mean_value

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

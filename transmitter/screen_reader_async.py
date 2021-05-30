import threading
import logging
import random
from ctypes import windll


class ScreenReaderAsync(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None,
                 index_range=[], queue=None, led_map=[]):
        super(ScreenReaderAsync, self).__init__()
        self.target = target
        self.name = name
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getdc
        self.dc = windll.user32.GetDC(None)
        self.index_range = index_range
        self.queue = queue
        self.led_map = led_map
        self.index_order = list(range(self.index_range[0], self.index_range[1]))
        random.shuffle(self.index_order)
        self.logger = logging.getLogger(self.name)

    def run(self):
        self.logger.info("Started screen reader")
        while True:
            for i in self.index_order:
                item = self.get_pixel(self.led_map[i])
                if item is not None:
                    self.queue.put(i, item)
        
    def get_pixel(self, coords):
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

import logging
from datetime import datetime
import win32gui, win32ui, win32con
from PIL import Image


class BitBltScreenshot:
    """
    Using the code from 
    https://stackoverflow.com/questions/48092655/memory-leak-with-createdcfromhandle-createcompatibledc
    """
    def __init__(self, bbox, hwnd=None):
        self.bbox = bbox
        self.hwnd = hwnd
        self.size = (self.bbox[2]-self.bbox[0], self.bbox[3]-self.bbox[1])
        self.position = (self.bbox[0], self.bbox[1])
        self.logger = logging.getLogger("BitBltScreenshot")
        self._grab()  # get the screenshot

    def getpixel(self, x, y):
        return self.screenshot.getpixel((x, y))

    def _grab(self):
        start = datetime.utcnow()
        self.hdc = win32gui.GetWindowDC(self.hwnd)
        self.dc = win32ui.CreateDCFromHandle(self.hdc)
        self.memdc = self.dc.CreateCompatibleDC()
        self.bitmap = win32ui.CreateBitmap()
        self.bitmap.CreateCompatibleBitmap(self.dc, self.size[0], self.size[1])
        self.memdc.SelectObject(self.bitmap)
        self.memdc.BitBlt((0, 0), self.size, self.dc, self.position, win32con.SRCCOPY)
        self.bits = self.bitmap.GetBitmapBits(True)
        self.screenshot = Image.frombuffer('RGB', self.size, self.bits, 'raw', 'BGRX', 0, 1)
        grabtime_ms = (datetime.utcnow() - start).total_seconds() * 1000
        self.logger.debug(f"grabbed a screenshot, duration={grabtime_ms}ms")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        win32gui.DeleteObject(self.bitmap.GetHandle())
        self.memdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hdc)
        self.logger.debug(f"exit called with exc_type={exc_type}, " +
                          f"exc_value={exc_value}, exc_traceback={exc_traceback}")

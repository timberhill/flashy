import mss
import logging


class MSSScreenshot(object):
    """Captures the screen using Python MSS,
    which is cross platform but intended for linux here.

    Docs: https://python-mss.readthedocs.io/index.html
    """
    def __init__(self, bbox):
        self.bbox = (bbox[0], bbox[1], bbox[2], bbox[3])
        self.logger = logging.getLogger("CGScreenshot")
        self.size = (self.bbox[2]-self.bbox[0], self.bbox[3]-self.bbox[1])
        self.position = (self.bbox[0], self.bbox[1])
        self._mss_instance = mss.mss()
        self._grab(bbox)

    def _grab(self, bbox):
        bbox_dict = dict(
            top=bbox[1],
            left=bbox[0],
            width=bbox[2] - bbox[0],
            height=bbox[3] - bbox[1]
        )
        self._data = self._mss_instance.grab(bbox_dict)

        self.width = self._data.width
        self.height = self._data.height

    def getpixel(self, x, y):
        return self._data.pixel(x, y)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._mss_instance.close()
        self.logger.debug(f"exit called with exc_type={exc_type}, " +
                          f"exc_value={exc_value}, exc_traceback={exc_traceback}")

import struct
import math
import logging

import Quartz.CoreGraphics as CG


class CGScreenshot(object):
    """Captures the screen using CoreGraphics, and provides access to
    the pixel values.

    From https://stackoverflow.com/questions/12978846/python-get-screen-pixel-value-in-os-x
    """
    def __init__(self, bbox):
        self.bbox = (bbox[0], bbox[1], bbox[2], bbox[3])
        self.logger = logging.getLogger("CGScreenshot")
        self.size = (self.bbox[2]-self.bbox[0], self.bbox[3]-self.bbox[1])
        self.position = (self.bbox[0], self.bbox[1])
        self._grab(bbox)

    def _grab(self, bbox):
        nearest_power_of_two = lambda n: 2**(int(math.log(n, 2)) + 1)
        region = CG.CGRectMake(
            self.position[0],
            self.position[1],
            nearest_power_of_two(self.size[0]),
            nearest_power_of_two(self.size[1])
        )

        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageNominalResolution)

        prov = CG.CGImageGetDataProvider(image)
        self._data = CG.CGDataProviderCopyData(prov)

        # Get width/height of image
        self.width = CG.CGImageGetWidth(image)
        self.height = CG.CGImageGetHeight(image)

    def getpixel(self, x, y):
        data_format = "BBBB"
        offset = 4 * ((self.width*int(round(y))) + int(round(x)))
        b, g, r, a = struct.unpack_from(data_format, self._data, offset=offset)
        return (r, g, b)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logger.debug(f"exit called with exc_type={exc_type}, " +
                          f"exc_value={exc_value}, exc_traceback={exc_traceback}")

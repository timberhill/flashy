import logging
from ctypes import windll


class ScreenReader:
    """
    Wrapper class for reading RGB values off the screen.

    Using 'windll.gdi32.GetPixel' function
    Docs: https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-getpixel

    Attributes:
        logger (logging.Logger): build-in python logger instance
    """
    def __init__(self):
        self._dc = windll.user32.GetDC(0)
        self.logger = logging.getLogger("ScreenReader")
        self.logger.debug(f"created")

    def get_pixel_value(self, coords):
        """Get an RGB value of a screen pixel

        Args:
            coords (tuple): x and y coordinates of the pixel

        Returns:
            tuple: 3 RGB values
        """
        return self._colorref_to_rgb(
            windll.gdi32.GetPixel(self._dc, *coords)
        )

    def get_average_pixel_value(self, topleft, bottomright=None, kind="mean"):
        """Get an average RGB value of a screen region using windll.gdi32.GetPixel

        Args:
            topleft (tuple): x and y coordinates of top left pixel of the region
            bottomright (tuple, optional): x and y coordinates of top left pixel of the region
            kind (str, optional): averaging kind, "median" or "mean"

        Returns:
            tuple: 3 RGB values
        """
        if bottomright is None:
            bottomright = (topleft[0]+1, topleft[1]+1)

        pixel_values = [
            self._colorref_to_rgb(windll.gdi32.GetPixel(self._dc, x, y))
            for x in range(topleft[0], bottomright[0])
            for y in range(topleft[1], bottomright[1])
        ]
        
        return self._average_rgb(arr=pixel_values, kind=kind)

    def _colorref_to_rgb(self, value):
        """Convert the COLORREF value into an RGB tuple.
        Docs: https://docs.microsoft.com/en-us/windows/win32/gdi/colorref

        Args:
            value (int): COLORREF value
            
        Returns:
            tuple: 3 RGB values
        """
        if value < 0:
            return (0, 0, 0)

        return tuple(int.to_bytes(
            value,
            length=3,
            byteorder="little"
        ))
    
    def _average_rgb(self, arr, kind):
        """Calculate an average value of an array of RGB values.

        Args:
            arr (list): list of RGB tuples (0..255)
            kind (str): averaging kind, "median" or "mean"
        
        Returns:
            tuple: 3 RGB values
        """
        if kind not in ["mean", "median"]:
            self.logger.warn(f"unexpected kind of averaging: '{kind}', calculating mean value instead")
            kind = "mean"

        if kind == "mean":
            return self._mean_rgb(arr)
        elif kind == "median":
            return self._median_rgb(arr)
    
    def _mean_rgb(self, arr):
        """Calculate a mean value of an array of RGB values.

        Args:
            arr (list): list of RGB tuples (0..255)

        Returns:
            tuple: 3 RGB values
        """
        N = len(arr)    
        return (
            sum(value[0] for value in arr) // N,
            sum(value[1] for value in arr) // N,
            sum(value[2] for value in arr) // N,
        )
    
    def _median_rgb(self, arr):
        """Calculate a median value of an array of RGB values.

        Args:
            arr (list): list of RGB tuples (0..255)
        
        Returns:
            tuple: 3 RGB values
        """
        N = len(arr) 
        r_sorted = sorted(value[0] for value in arr)
        g_sorted = sorted(value[1] for value in arr)
        b_sorted = sorted(value[2] for value in arr)

        index = (N - 1) // 2
        
        if N % 2:
            return (r_sorted[index], g_sorted[index], b_sorted[index])
        else:
            return (
                r_sorted[index] + r_sorted[index + 1] // 2,
                g_sorted[index] + g_sorted[index + 1] // 2,
                b_sorted[index] + b_sorted[index + 1] // 2
            )

import logging
import time
from ctypes import windll


class ScreenReader:
    """
    Wrapper class for reading RGB values off the screen.

    Using 'windll.gdi32.GetPixel' function
    Docs: https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-getpixel
    """
    def __init__(self):
        self._dc = windll.user32.GetDC(0)
        self.logger = logging.getLogger("ScreenReader")
        self.logger.debug(f"created")

    def get_pixel_value(self, coords):
        """
        Get an RGB value of a scren pixel

        Parameters:

            coords, tuple:
                x and y coordinates of the pixel
        """
        return tuple(int.to_bytes(
            windll.gdi32.GetPixel(self._dc, *coords),
            length=3,
            byteorder="little"
        ))

    def get_region_value(self, topleft, bottomright, kind="mean"):
        """
        Get an RGB value of a screen region using windll.gdi32.GetPixel

        Parameters:

            topleft, tuple:
                x and y coordinates of top left pixel of the region

            bottomright, tuple:
                x and y coordinates of top left pixel of the region

            kind, str:
                averaging kind, "median" or "mean"
        """
        start = time.time()

        values = []
        for x in range(topleft[0], bottomright[0]):
            for y in range(topleft[1], bottomright[1]):
                values.append(windll.gdi32.GetPixel(self._dc, x, y))
        
        read_ms, len_values = (time.time()-start)*1000, len(values)
        self.logger.debug(f"read {len_values} pixels in {read_ms:0.1f}ms ({read_ms/len_values:0.1f} ms/px)")
        
        return self._average_rgb(
            arr=[self._colorref_to_rgb(value) for value in values],
            kind=kind
        )

    def _colorref_to_rgb(self, value):
        """
        Convert the COLORREF value into an RGB tuple.
        Docs: https://docs.microsoft.com/en-us/windows/win32/gdi/colorref

        Parameters:

            value, int:
                COLORREF value
            
        Returns:

            rgb, tuple:
                a three-part RGB tuple
        """
        if value < 0:
            return (0, 0, 0)

        return tuple(int.to_bytes(
            value,
            length=3,
            byteorder="little"
        ))
    
    def _average_rgb(self, arr, kind):
        """
        Calculate an average value of an array of RGB values.

        Parameters:

            arr, list:
                list of RGB tuples (0..255)

            kind, str:
                averaging kind, "median" or "mean"
        
        Returns:

            tuple, an average RGB
        """
        if kind not in ["mean", "median"]:
            self.logger.warn(f"unexpected kind of averaging: '{kind}', calculating mean value instead")
            kind = "mean"

        if kind == "mean":
            return self._mean_rgb(arr)
        elif kind == "median":
            return self._median_rgb(arr)
    
    def _mean_rgb(self, arr):
        """
        Calculate a mean value of an array of RGB values.

        Parameters:

            arr, list:
                list of RGB tuples (0..255)

        Returns:

            tuple, a mean RGB
        """
        N = len(arr)    
        return (
            sum(value[0] for value in arr) // N,
            sum(value[1] for value in arr) // N,
            sum(value[2] for value in arr) // N,
        )
    
    def _median_rgb(self, arr):
        """
        Calculate a median value of an array of RGB values.

        Parameters:

            arr, list:
                list of RGB tuples (0..255)
        
        Returns:

            tuple, a median RGB
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

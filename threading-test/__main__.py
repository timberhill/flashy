import logging
import sys
from ctypes import windll
from threading import Thread

logging.basicConfig(
    level="INFO",
    format='time=%(asctime)s, location=%(filename)s:%(lineno)d, message=\"%(message)s\"',
    handlers=[
        logging.FileHandler(filename='flashy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


def screenreader(identifier):
    """Get an RGB value of a screen pixel

    Args:
        coords (tuple): x and y coordinates of the pixel

    Returns:
        tuple: 3 RGB values
    """
    dc = windll.user32.GetDC(0)
    logger = logging.getLogger("ScreenReader")
    logger.info(f"identifier={identifier} created")
    while True:
        value = windll.gdi32.GetPixel(dc, 720, 1385)
        logger.info(f"value={value}")

for i in range(3):
    t = Thread(target=screenreader, args=(i,))
    t.start()

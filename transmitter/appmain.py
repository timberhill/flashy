import logging
import sys
import time
import random
import serial.tools.list_ports

from .transmitter import SerialTransmitter
from .screenreader import ScreenReader


class AppMain:
    """Main class that handles the high level logic.

    Attributes:
        serial (transmitter.SerialTransmitter): object handling the serial communication with the board
        screen (screenreader.Screenreader): object handling reading the pixel data off a screen
        logger (logging.Logger): build-in python logger instance

    Args:
        settings (dict): a dictionary with the app settings
    """
    def __init__(self, settings):
        if not hasattr(settings, "port") or settings.port is None:
            settings.port = self.serial_ports[0].device

        self.logger = logging.getLogger("AppMain")
        self.between_frames_ms = settings.between_frames_ms
        self.screen = ScreenReader()
        self.serial = SerialTransmitter(
            port=settings.port,
            baud=settings.baud,
            strip_size=settings.strip_size
        )

        self.logger.info(f"started")
    
    @property
    def serial_ports(self):
        """Get a list of avaliable serial devices.

        Returns:
            list: list of dictionaries like {"device": "COM1", "description": "something here"}
        """
        return list(serial.tools.list_ports.comports())
    
    def start(self):
        """Function containing the main loop.
        Starts reading the pixel values off the screen and sending them to the board.
        """
        while True:
            start = time.time()
            mappings = [(i, (1280 + 50*(i-7), 1385)) for i in range(15)]
            random.shuffle(mappings)

            for i, coords in mappings:
                rgb = self.screen.get_average_pixel_value(coords, (coords[0]+1, coords[1]+1), "mean")
                self.serial.send([(i,) + rgb])

            read_ms, len_values = (time.time()-start)*1000, len(mappings)
            self.logger.debug(f"read {len_values} pixels in {read_ms:0.1f}ms ({read_ms/len_values:0.1f} ms/px)")

            # wait until the next frame
            if self.between_frames_ms > 0:
                time.sleep(self.between_frames_ms / 1000)

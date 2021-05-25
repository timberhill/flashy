import logging
from threading import Thread
import time
import random
import serial.tools.list_ports

from .transmitter import SerialTransmitter
from .screenreader import ScreenReader
from .serial_buffer import SerialBuffer


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
        self.settings = settings
        self.buffer = SerialBuffer(length=self.settings.strip_size)
        self.screen = ScreenReader()
        self.serial = SerialTransmitter(
            port=self.settings.port,
            baud=self.settings.baud,
            strip_size=self.settings.strip_size
        )

        self.screenreader_threads = [None] * self.settings.screenreader_threads
        self.transmitter_thread = None

        self.logger.info(f"started")
    
    @property
    def serial_ports(self):
        """Get a list of avaliable serial devices.

        Returns:
            list: list of dictionaries like {"device": "COM1", "description": "something here"}
        """
        return list(serial.tools.list_ports.comports())

    def _screenreader_worker(self, buffer, index_from, index_to):
        while True:
            indices = list(range(index_from, index_to))
            random.shuffle(indices)
            for i in indices:
                value = self.screen.get_average_pixel_value(self.settings.profile.map[i], "mean")
                if all([x > 0 for x in value]):
                    buffer.set(i, value)

    def _transmitter_worker(self, buffer):
        while True:
            if self.settings.between_frames_ms > 0:
                time.sleep(self.settings.between_frames_ms / 1000.0)
                
            indices = list(range(self.settings.strip_size))
            random.shuffle(indices)
            # items = [(i, buffer.get(i)) for i in range(self.settings.strip_size)]
            # strip_data = [(i,) + item.value for i, item in items if not item.was_retrieved]
            # self.serial.send(strip_data)
            for i in indices:
                item = buffer.get(i)
                if not item.was_retrieved:
                    # self.logger.info(f">>> {i} > {item.value}")
                    self.serial.send([(i,) + item.value])

    def start(self):
        """Function containing the main loop.
        Starts reading the pixel values off the screen and sending them to the board.
        """
        self.transmitter_thread = Thread(target=self._transmitter_worker, args=(self.buffer,))
        self.transmitter_thread.start()
        
        for i in range(self.settings.screenreader_threads):
            index_from = i * self.settings.strip_size // self.settings.screenreader_threads
            index_to = (i+1) * self.settings.strip_size // self.settings.screenreader_threads
            self.screenreader_threads[i] = Thread(target=self._screenreader_worker, args=(self.buffer, index_from, index_to))
            self.screenreader_threads[i].start()

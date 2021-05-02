import logging
import sys
import time
import serial.tools.list_ports

from transmitter import Transmitter
from screenreader import ScreenReader


class AppMain:
    """
    Main class that handles the high level logic.
    """
    def __init__(self, settings):
        logging.basicConfig(
            level=settings.get("log_level", "INFO"),
            format='time=%(asctime)s, level=%(levelname)s, location=%(filename)s:%(lineno)d, message=\"%(message)s\"',
            handlers=[
                logging.FileHandler(filename='flashy.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.serial = Transmitter(
            port=settings["port"],
            baud=settings["baud"],
            strip_size=settings["strip_size"]
        )
        self.screen = ScreenReader()

        self.logger = logging.getLogger("AppMain")
        self.logger.info(f"started")
    
    def start(self):
        """
        Function containing the main loop.
        """
        while True:  # this is all hardcoded for now
            r, g, b = self.screen.get_region_value((1024, 510), (1025, 520), "mean")
            self.serial.send([(0, r, g, b)])
            time.sleep(0.01)


def serial_ports():
    """
    Get a list of avaliable serial devices.

    Returns:

        list of dictionaries like {"device": "COM1", "description": "something here"}
    """
    return [
        dict(
            device=port.device,
            description=port.description
        )
        for port in list(serial.tools.list_ports.comports())
    ]


if __name__ == "__main__":
    debug = 1

    main = AppMain(settings=dict(
        port=serial_ports()[0]["device"],
        baud=9600,
        strip_size=1,
        log_level="INFO" if debug == 0 else "DEBUG"
    )).start()

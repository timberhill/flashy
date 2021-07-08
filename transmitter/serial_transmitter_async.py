import random
import threading
import logging
from serial import Serial
import time


class SerialTransmitterAsync(threading.Thread):
    """Class getting values from the queue and sending them to serial port in a separate thread.

    Args:
        name (str): name of the thread
        queue (queue.Queue): queue to add the values to
        led_map (list): LED index to pixel coordinates mapping from the profile
        port (str): serial port name
        baud (int): baud rate of the serial communication
    
    Attributes:
        name (str): name of the thread
        serial (serial.Serial): serial communication object
        queue (queue.Queue): queue to add the values to
        led_map (list): LED index to pixel coordinates mapping from the profile
        index_order (list): list of indices in the index_range in a random order
        logger (Logger): logger object used to write logs from this thread
    """
    def __init__(self, name=None, queue=None, port=None, baud=9600, frame_delay=1):
        super(SerialTransmitterAsync,self).__init__()
        self.name = name
        self.queue = queue
        self.port = port
        self.baud = baud
        self.frame_delay = frame_delay
        self.serial = None
        self.index_order = list(range(self.queue.length))
        self.error_logged = False  # to not flood the console with errors if disconnected
        random.shuffle(self.index_order)
        self.logger = logging.getLogger(self.name)

    def _connect(self):
        self.serial = Serial(self.port, self.baud)

    def run(self):
        """Run the loop of getting values form the queue and sending them to the serial port.
        """
        self.logger.debug("Started serial transmitter")
        while True:
            time.sleep(self.frame_delay/1000)
            for i in self.index_order:
                if not self.queue.empty(i):
                    item = self.queue.get(i)
                    self.send_value((i,) + item)

    def send_value(self, value):
        """Format and send the rgb value to the serial port.

        Args:
            value (tuple/list): list of values to send in the single package

        Returns:
            formatted string that was sent to the serial
        """
        string_data = ">" + "".join([str(x).zfill(3) for x in value])

        try:
            if self.serial is None:
                self._connect()
                self.logger.info(f"Connected to {self.port}")
            self.serial.write(bytes(string_data, "utf-8"))
            self.error_logged = False
        except IOError as e:
            if not self.error_logged:
                self.logger.error(f"Can't connect to the receiver: {e}")
                self.error_logged = True
            self.serial = None
            time.sleep(1)

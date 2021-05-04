import logging
from serial import Serial


class SerialTransmitter:
    """
    Wrapper for the serial communication with the receiver.

    Attributes:
        strip_size (int): the number of LEDs in the strip
        port (str): serial port name
        serial (serial.Serial): serial communication object
        logger (logging.Logger): build-in python logger instance
    
    Args:
        port (str): serial port name
        baud (int): serial BAUD rate
    """
    def __init__(self, port, baud=9600):
        self.port = port
        self.serial = Serial(port, baud)
        self.logger = logging.getLogger("SerialTransmitter")
        self.logger.debug(f"created: port={port}, baud={baud}, strip_size={strip_size}")

    def _output_format(self, values):
        """
        Convert the values into a formatted string to send over serial.

        Args:
            values (tuple/list): 4 values - for the number of an LED and the RGB values.

        Returns:
            str: string representation to send over serial
        """
        return ">" + "".join([str(x).zfill(3) for x in values])


    def send(self, data):
        """
        Send all the RGB values for all the LEDs.
        Serial data format: ">IIIRRRGGGBBB"

        Args:
            data (list): a list of tuples containing the LED index and RGB values in a tuple.
        """
        self.logger.debug(f"sending {len(data)} items to {self.port}")
        for i, item in enumerate(data):
            string_data = self._output_format(item)
            self.logger.debug(f"sending {i+1}/{len(data)}: '{string_data}'")
            self.serial.write(bytes(string_data, "utf-8"))

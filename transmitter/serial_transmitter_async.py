import random
import threading
import logging
from serial import Serial


class SerialTransmitterAsync(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None,
                 queue=None, port=None, baud=9600):
        super(SerialTransmitterAsync,self).__init__()
        self.target = target
        self.name = name
        self.serial = Serial(port, baud)
        self.queue = queue
        self.index_order = list(range(15))
        random.shuffle(self.index_order)
        self.logger = logging.getLogger(self.name)

    def run(self):
        self.logger.info("Started serial transmitter")
        while True:
            for i in self.index_order:
                if not self.queue.empty(i):
                    item = self.queue.get(i)
                    self.send_value((i,) + item)

    def send_value(self, value):
        string_data = ">" + "".join([str(x).zfill(3) for x in value])
        self.logger.debug(f"Sending data to {self.serial.port}: '{string_data}'")
        self.serial.write(bytes(string_data, "utf-8"))
        return string_data

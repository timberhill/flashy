import logging
import threading


class SerialBufferItem:
    def __init__(self, value):
        self._value = value
        self.was_retrieved = False
        self.logger = logging.getLogger("SerialBufferItem")
        self.logger.debug(f"created")

    @property
    def value(self):
        self.was_retrieved = True
        return self._value

    def update(self, value):
        self.was_retrieved = False
        self._value = value


class SerialBuffer:
    def __init__(self, length=1, initial_value=(0,0,0)) -> None:
        self.mutex = threading.Lock()
        self.length = length
        self.items = [SerialBufferItem(initial_value) for i in range(length)]
        self.logger = logging.getLogger("SerialBuffer")
        self.logger.debug(f"created")
    
    def _validate_index(self, index):
        if index >= self.length:
            raise ValueError(f"Got an index ({index}) that is bigger than the serial queue length ({self.length}).")

    def _validate_rgb(self, rgb):
        if len(rgb) != 3:
            raise ValueError(f"'rgb' argument must have length of 3.")
    
    def set(self, index, rgb):
        self._validate_index(index)
        self._validate_rgb(rgb)
        with self.mutex:
            self.items[index].update(rgb)
    
    def get(self, index):
        self._validate_index(index)
        with self.mutex:
            return self.items[index]

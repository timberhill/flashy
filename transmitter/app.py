import time
import logging
from . import QueueArray, ScreenReaderAsync, SerialTransmitterAsync


class FlashyApp:
    """Main flashy transmitter app.
    
    Attributes:
        settings (transmitter.settings.Settings): settings object
        logger (logging.Logger): settings logger object
        readers (list[ScreenReaderAsync]): list of screen reader threads
        transmitter (SerialTransmitterAsync): serial transmitter thread

    Args:
        path (str, optional): path to settings.json, defaults to 'settings/settings.json'
    """
    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger("FlashyApp")
        self.readers = []
        self.setup()

    def setup(self):
        """Set up the app and create all the threads.
        """
        # set up the queue
        self.queue = QueueArray(length=self.settings.strip_size, size=5)

        # create the reader threads
        for i in range(self.settings.threads):
            index_range = [
                i * self.settings.strip_size//self.settings.threads,
                (i+1) * self.settings.strip_size//self.settings.threads
            ]

            reader = ScreenReaderAsync(
                name=f"ScreenReader_{index_range[0]}_{index_range[1]}",
                index_range=index_range,
                queue=self.queue,
                settings=self.settings
            )
            reader.daemon = True
            self.readers.append(reader)

        # create the transmitter thread
        self.transmitter = SerialTransmitterAsync(
            name=f"SerialTransmitter_{self.settings.port}",
            queue=self.queue,
            port=self.settings.port,
            baud=self.settings.baud
        )
        self.transmitter.daemon = True

        # keep the main thread alive while the daemons are working
        self.logger.info("All threads are set up")
    
    def start(self):
        """Start the daemon threads and wait in the main thread indefinitely.
        """
        self.transmitter.start()
        for reader in self.readers:
            reader.daemon = True
            reader.start()
        
        self.logger.info("All threads are running!")

        # wait indefinitely
        while True:
            time.sleep(3600)

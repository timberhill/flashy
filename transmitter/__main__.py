"""
Entry point of flashy
"""

import logging
import sys
import time
import serial.tools.list_ports

from .queue_array import QueueArray
from .screen_reader_async import ScreenReaderAsync
from .serial_transmitter_async import SerialTransmitterAsync
from .settings import Settings


if __name__ == "__main__":

    # read the settings file
    settings = Settings("settings/settings.json")

    handlers = [logging.StreamHandler(sys.stdout),]
    if settings.logfile is not None:
        handlers += logging.FileHandler(filename=settings.logfile),
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s:%(name)s:%(filename)s:%(lineno)d - %(message)s",
        handlers=handlers
    )
    logger = logging.getLogger("App")

    logger.info("Starting with settings below:")

    if settings.port is None:
        settings.port = serial.tools.list_ports.comports()[0].device
        logger.info(f"Serial port: {settings.port} (autodetected)")
    else:
        logger.info(f"Serial port: {settings.port}")

    logger.info(f"Baud rate:   {settings.baud}")
    logger.info(f"Threads:     {settings.threads}")
    logger.info(f"Strip size:  {settings.strip_size}")
    logger.info(f"Log level:   {settings.log_level}")
    logger.info(f"Profile:     {settings.profile.description}")
    logger.info(f"Log file:    {settings.logfile}")

    # set up the queue
    queue = QueueArray(length=settings.strip_size, size=5)

    # create the reader threads
    for i in range(settings.threads):
        index_range = [
            i * settings.strip_size//settings.threads,
            (i+1) * settings.strip_size//settings.threads
        ]

        reader = ScreenReaderAsync(
            name=f"ScreenReader{i}:{index_range}",
            index_range=index_range,
            queue=queue,
            settings=settings
        )
        reader.daemon = True
        reader.start()

    # create the transmitter thread
    transmitter = SerialTransmitterAsync(
        name="SerialTransmitter",
        queue=queue,
        port=settings.port,
        baud=settings.baud
    )
    transmitter.daemon = True
    transmitter.start()

    # keep the main thread alive while the daemons are working
    logger.info("All threads are set up and running!")
    while True:
        time.sleep(3600)

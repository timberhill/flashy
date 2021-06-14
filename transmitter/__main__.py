"""
Entry point of flashy
"""

import logging
import sys
import serial.tools.list_ports

from . import Settings, FlashyApp


if __name__ == "__main__":

    # read the settings file
    settings = Settings("settings/settings.json")

    handlers = [logging.StreamHandler(sys.stdout),]
    if settings.logfile is not None:
        handlers += logging.FileHandler(filename=settings.logfile),
    
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(levelname)s - %(name)s:%(filename)s:%(lineno)d - %(message)s",
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

    app = FlashyApp(settings)
    app.start()

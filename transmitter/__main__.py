"""
Entry point of flashy
"""

import logging
import sys
import serial.tools.list_ports
import time

from . import Settings, FlashyApp


if __name__ == "__main__":
    settings_path = "settings/settings.json"

    # read the settings file
    settings = Settings(settings_path)

    handlers = [logging.StreamHandler(sys.stdout),]
    if settings.logfile is not None:
        handlers += logging.FileHandler(filename=settings.logfile),
    
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s:%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
        handlers=handlers
    )
    logger = logging.getLogger("App")

    # find first available serial port
    autodetected = settings.port is None
    while settings.port is None:
        comports = serial.tools.list_ports.comports()
        if len(comports) > 1:
            logger.info(f"Serial devices connected:")
            for comport in comports:
                logger.info(f"   -- {comport.device}: {comport.description}")
        if len(comports) == 0:
            logger.info(f"No serial devices connected")
            time.wait(3)
        else:
            settings.port = serial.tools.list_ports.comports()[0].device

    logger.info(f"Starting with settings from {settings_path}")
    logger.info(f"  -- Serial port: {settings.port}" +
                f"{' (autodetected)' if autodetected else ''}")
    logger.info(f"  --   Baud rate: {settings.baud}")
    logger.info(f"  --     Threads: {settings.threads}")
    logger.info(f"  --  Strip size: {settings.strip_size}")
    logger.info(f"  --   Log level: {settings.log_level}")
    logger.info(f"  --     Profile: {settings.profile.description}")
    logger.info(f"  --    Log file: {settings.logfile}")

    app = FlashyApp(settings)
    app.start()

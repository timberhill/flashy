import sys
import logging

from .appmain import AppMain
from .settings import Settings


# read the settings file
settings = Settings("settings/settings.json")

logging.basicConfig(
    level=settings.log_level,
    format='time=%(asctime)s, level=%(levelname)s, location=%(filename)s:%(lineno)d, message=\"%(message)s\"',
    handlers=[
        logging.FileHandler(filename='flashy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Start the app
AppMain(settings).start()

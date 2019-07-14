import os
import logging

import connection.client_core
import connection.server_core
from config.config import Settings

# change working dir to this directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

settings = Settings(str(os.path.join('config', 'config.ini')))

log_level = getattr(logging, settings.log_level)
logging.basicConfig(level=log_level)

if settings.isServer:
    logging.info('Starting Server')
    connection.server_core.main(settings)
else:
    logging.info('Starting Client')
    connection.client_core.main(settings)

import os

import connection.client_core
import connection.server_core
from config.config import Settings

# change working dir to this directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

settings = Settings(str(os.path.join('config', 'config.ini')))

if settings.isServer:
    # you are the server
    connection.server_core.main(settings)
else:
    # you are a client
    connection.client_core.main(settings)

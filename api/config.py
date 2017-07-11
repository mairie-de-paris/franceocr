import logging
import logging.handlers
import os
import sys

DEBUG = True
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))

# Grabs the folder where the script runs.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.abspath(BASEDIR + "/../uploads")
ALLOWED_MIME = set([
    'image/jpeg',
    'image/png',
])
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

# ===================
#       LOGGING
# ===================
formatter = logging.Formatter(
    "%(asctime)s - module:%(module)s - [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

# Console logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File logging
file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(BASEDIR, '../logs/server.log'),
    when='midnight',
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

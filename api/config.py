import os, logging

DEBUG = True
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT', '5000'))

logging.basicConfig(
    filename=os.getenv('SERVICE_LOG', 'server.log'),
    level=logging.DEBUG,
    format='%(levelname)s: %(asctime)s pid:%(process)s module:%(module)s %(message)s',
    datefmt='%d/%m/%y %H:%M:%S',
)

# Grabs the folder where the script runs.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.abspath(BASEDIR + "/../uploads")
ALLOWED_MIME = set([
    'image/jpeg',
    'image/png',
])
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

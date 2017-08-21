import logging
import logging.handlers
import os

DEBUG = True
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))

# Grabs the folder where the script runs.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.abspath(BASEDIR + "/../uploads")
ALLOWED_MIME = set([
    'image/jpeg',
    'image/png',
    'application/pdf',
])
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

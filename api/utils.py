import requests

from io import BytesIO
from PIL import Image

from config import ALLOWED_MIME


def get_image(filename):
    return Image.open(filename)


def get_image_from_url(url):
    return Image.open(BytesIO(requests.get(url).content))


def allowed_file(file):
    return file.mimetype in ALLOWED_MIME

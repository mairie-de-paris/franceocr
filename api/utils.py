import json
import requests

from bson import json_util
from io import BytesIO
from PIL import Image

from config import ALLOWED_MIME


def get_image(filename):
    return Image.open(filename)


def get_image_from_url(url):
    return Image.open(BytesIO(requests.get(url).content))


def allowed_file(file):
    return file.mimetype in ALLOWED_MIME


def is_pdf(file):
    return file.mimetype == "application/pdf"


def to_json(data):
    return json.dumps(data, default=json_util.default)

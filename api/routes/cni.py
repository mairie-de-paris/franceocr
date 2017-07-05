import cv2
import os

from flask import Blueprint, current_app, jsonify, request
from franceocr import cni_process
from franceocr.cni.exceptions import (
    InvalidChecksumException,
    InvalidMRZException
)
from franceocr.exceptions import ImageProcessingException, InvalidOCRException
from uuid import uuid4

from exceptions import InvalidUsageException
from utils import allowed_file

cni_blueprint = Blueprint('cni', __name__)


@cni_blueprint.errorhandler(ImageProcessingException)
@cni_blueprint.errorhandler(InvalidChecksumException)
@cni_blueprint.errorhandler(InvalidMRZException)
@cni_blueprint.errorhandler(InvalidOCRException)
def handle_errors(error):
    response = jsonify({
        'exception': type(error).__name__,
        'message': error.args[0],
    })
    response.status_code = 422
    return response


@cni_blueprint.route('/cni/scan', methods=['POST'])
def cni_scan():
    image_file = request.files.get('image')

    if not image_file:
        raise InvalidUsageException('No file provided')

    if not allowed_file(image_file):
        raise InvalidUsageException('Invalid file type')

    filename = str(uuid4()) + os.path.splitext(image_file.filename)[1]
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    image_file.save(filepath)

    # image = np.array(Image.open(image_file.stream))
    # image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # print(image.shape)
    # print(image.mean(axis=0).mean(axis=0))

    # FIXME
    image = cv2.imread(filepath)

    if min(image.shape[0], image.shape[1]) < 900:
        raise InvalidUsageException('Image must be at least 900x900 pixels')

    cni_data = cni_process(image)

    return jsonify({
        'data': cni_data,
        'image_path': 'uploads/' + filename
    })

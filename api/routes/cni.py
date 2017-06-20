import os

from flask import Blueprint, jsonify
from franceocr import process_cni
from werkzeug.utils import secure_filename

from utils import allowed_file

cni_blueprint = Blueprint('cni', __name__)


@cni_blueprint.route('/cni/scan', methods=['POST'])
def cni_scan():
    image = request.files.get('image')

    if not image:
        raise InvalidUsageException('No file provided')

    if not allowed_file(image):
        raise InvalidUsageException('Invalid file type')

    filename = secure_filename(image.filename)
    image.save(os.path.join(server.config['UPLOAD_FOLDER'], filename))

    output = ''

    return jsonify({
        'data': output
    })

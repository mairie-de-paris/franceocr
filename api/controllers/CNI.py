import os

from Flask import jsonify
from franceocr import process_cni
from werkzeug.utils import secure_filename

from ..app import app
from ..utils import allowed_file


@app.route('/api/CNI/scan', methods=['POST'])
def cni_scan():
    image = request.files.get('image')

    if not image:
        raise InvalidUsageException('No file provided')

    if not allowed_file(image):
        raise InvalidUsageException('Invalid file type')

    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    output = ''

    return jsonify({
        'output': output
    })

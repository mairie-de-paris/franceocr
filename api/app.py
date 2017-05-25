import os
import logging
from flask import Flask, request, jsonify, render_template

from ocr import process_image
from utils import get_image_from_url

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/api/documents/cni', methods=["POST"])
def cni():
    url = request.form['image_url']
    if not url:
        raise InvalidUsage('Url not provided')

    image = get_image_from_url(url)
    if 'jpg' in url:
        output = process_image(image)
        return jsonify({
            "output": output
        })
    else:
        raise InvalidUsage('Only jpeg')


if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )
    app.logger.setLevel(logging.INFO)
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.info('errors')


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port)

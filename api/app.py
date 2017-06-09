import os
import logging
from flask import Flask, request, jsonify, render_template

from ocr import process_image
from utils import get_image_from_url

app = Flask(__name__)

# Load configuration
app.config.from_object('.config.DefaultSettings')
app.config.from_pyfile('settings.cfg')  # , silent=True)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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

from flask import Flask, jsonify
from flask_cors import CORS

import config
from database import mongo
from exceptions import InvalidUsageException
from routes import cni_blueprint, common_blueprint, front_blueprint


server = Flask(__name__)
server.debug = config.DEBUG

mongo.init_app(server)

CORS(
    server,
    resources={r"/*": {"origins": "*"}},
    allow_headers=['Content-Type', 'X-Requested-With', 'Authorization']
)

# Load configuration
server.config.from_object(config)


@server.errorhandler(InvalidUsageException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


server.register_blueprint(cni_blueprint)
server.register_blueprint(common_blueprint)
server.register_blueprint(front_blueprint)

if __name__ == '__main__':
    server.run(host=config.HOST, port=config.PORT)

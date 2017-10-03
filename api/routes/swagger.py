import os

from flask import Blueprint, jsonify, current_app, send_from_directory
from flask_swagger import swagger

swagger_blueprint = Blueprint("swagger", __name__)


@swagger_blueprint.route("/api/swagger.json")
def swagger_api():
    swag = swagger(current_app)
    swag["info"]["version"] = "1.0"
    swag["info"]["title"] = "FranceOCR API"
    return jsonify(swag)


@swagger_blueprint.route("/api/swagger")
@swagger_blueprint.route("/api/<path:filename>")
def swagger_html(filename="index.html"):
    return send_from_directory(os.path.abspath(current_app.config["BASEDIR"] + "/static/swagger"), filename)

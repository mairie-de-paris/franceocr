import os.path

from flask import Blueprint, jsonify, current_app, send_from_directory

front_blueprint = Blueprint('front', __name__)


@front_blueprint.route('/')
def index():
    return send_from_directory(os.path.abspath(current_app.config["BASEDIR"] + "/static/front"), "index.html")


@front_blueprint.route('/<path:filename>')
def asset_file(filename):
    return send_from_directory(os.path.abspath(current_app.config["BASEDIR"] + "/static/front"), filename)

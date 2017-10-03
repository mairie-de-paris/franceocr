from flask import Blueprint, current_app, send_from_directory

common_blueprint = Blueprint("common", __name__)


@common_blueprint.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

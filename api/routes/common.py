from flask import Blueprint, jsonify, current_app

common_blueprint = Blueprint('common', __name__)


@common_blueprint.route('/routes')
def list_routes():
    output = []
    for rule in current_app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = "{:50s} {:20s}".format(str(rule), methods)
        output.append(line)
    return jsonify(routes=output)

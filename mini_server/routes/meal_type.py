# meal_type_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from mini_server.service.meal_type_service import (
    get_name_by_id, get_id_by_name,
    get_name_by_time, get_current_meal_type
)

type_bp = Blueprint('meal_types', __name__, url_prefix='/meal_types')

@type_bp.route('/id/<int:meal_type_id>', methods=['GET'])
def get_meal_name(meal_type_id):
    name = get_name_by_id(meal_type_id)
    return jsonify({'name': name}) if name else ('', 404)

@type_bp.route('/name/<string:name>', methods=['GET'])
def get_meal_id(name):
    meal_id = get_id_by_name(name)
    return jsonify({'id': meal_id}) if meal_id else ('', 404)

@type_bp.route('/time/<string:time_str>', methods=['GET'])
def get_meal_by_time(time_str):
    name = get_name_by_time(time_str)
    return jsonify({'meal_type': name}) if name else ('', 400)

@type_bp.route('/current', methods=['GET'])
def get_current_meal():
    name = get_current_meal_type()
    return jsonify({'current_meal': name})
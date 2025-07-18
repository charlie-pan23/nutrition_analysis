# food_routes.py
from flask import Blueprint, request, jsonify
from mini_server.service.food_service import add_food, get_food_by_id, get_food_by_name, get_all_foods, update_food, delete_food

food_bp = Blueprint('food', __name__, url_prefix='/foods')

@food_bp.route('', methods=['POST'])
def create_food():
    data = request.get_json()
    food = add_food(**data)
    return jsonify(food.to_dict()), 201 if food else 400

@food_bp.route('/<int:food_id>', methods=['GET'])
def get_food(food_id):
    food = get_food_by_id(food_id)
    return jsonify(food.to_dict()) if food else ('', 404)

@food_bp.route('/name/<string:food_name>', methods=['GET'])
def search_food(food_name):
    food = get_food_by_name(food_name)
    return jsonify(food.to_dict()) if food else ('', 404)

@food_bp.route('', methods=['GET'])
def list_foods():
    foods = get_all_foods()
    return jsonify([food.to_dict() for food in foods])

@food_bp.route('/<int:food_id>', methods=['PUT'])
def modify_food(food_id):
    data = request.get_json()
    updated = update_food(food_id, **data)
    return jsonify(updated.to_dict()) if updated else ('', 404)

@food_bp.route('/<int:food_id>', methods=['DELETE'])
def remove_food(food_id):
    success = delete_food(food_id)
    return '', 204 if success else 404
# api/food_routes.py
from flask import Blueprint, jsonify, request
# 导入食物服务中的所有功能
from app.services.food_service import add_food, get_food_by_id, get_food_by_name, get_all_foods, update_food, delete_food
import logging

logger = logging.getLogger(__name__)

# 创建一个蓝图实例
food_bp = Blueprint('food_bp', __name__, url_prefix='/foods')
# 如果您希望版本化 API，可以这样设置：
# food_bp = Blueprint('food_bp', __name__, url_prefix='/api/v1/foods')


@food_bp.route('/', methods=['POST'])
def api_add_food():
    data = request.json
    if not data or 'name' not in data or 'calories' not in data:
        return jsonify({"error": "缺少食物名称或热量"}), 400

    # 检查是否已存在同名食物
    existing_food = get_food_by_name(data['name'])
    if existing_food:
        return jsonify({"message": f"食物 '{data['name']}' 已存在。", "food": existing_food.to_dict()}), 200

    new_food = add_food(**data)
    if new_food:
        return jsonify({"message": "食物添加成功", "food": new_food.to_dict()}), 201
    return jsonify({"error": "食物添加失败"}), 500

@food_bp.route('/<int:food_id>', methods=['GET'])
def api_get_food_by_id(food_id):
    """根据 ID 获取食物"""
    food = get_food_by_id(food_id)
    if food:
        return jsonify({"message": "食物获取成功", "food": food.to_dict()}), 200
    return jsonify({"error": f"食物 ID: {food_id} 未找到"}), 404

@food_bp.route('/name/<string:food_name>', methods=['GET'])
def api_get_food_by_name(food_name):
    """根据名称获取食物"""
    food = get_food_by_name(food_name)
    if food:
        return jsonify({"message": "食物获取成功", "food": food.to_dict()}), 200
    return jsonify({"error": f"食物名称: '{food_name}' 未找到"}), 404

@food_bp.route('/', methods=['GET'])
def api_get_all_foods():
    foods = get_all_foods()
    return jsonify({"message": "所有食物获取成功", "foods": [f.to_dict() for f in foods]}), 200

@food_bp.route('/<int:food_id>', methods=['PUT'])
def api_update_food(food_id):
    data = request.json
    if not data:
        return jsonify({"error": "请求体为空"}), 400
    updated_food = update_food(food_id, **data)
    if updated_food:
        return jsonify({"message": "食物更新成功", "food": updated_food.to_dict()}), 200
    return jsonify({"error": "食物更新失败或食物不存在"}), 404

@food_bp.route('/<int:food_id>', methods=['DELETE'])
def api_delete_food(food_id):
    if delete_food(food_id):
        return jsonify({"message": f"食物 ID: {food_id} 删除成功"}), 200
    return jsonify({"error": "食物删除失败或食物不存在"}), 404

# api/meal_type_routes.py
from flask import Blueprint, jsonify, request
from app.services.meal_type_service import (
    add_meal_type,
    get_meal_type_by_id,
    get_meal_type_by_name,
    get_all_meal_types,
    get_meal_types_by_time_description # 新增导入
)

meal_type_bp = Blueprint('meal_type_bp', __name__, url_prefix='/meal_types')

@meal_type_bp.route('/', methods=['POST'])
def api_add_meal_type():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "缺少餐食类型名称"}), 400

    existing_type = get_meal_type_by_name(data['name'])
    if existing_type:
        return jsonify({"message": f"餐食类型 '{data['name']}' 已存在。", "meal_type": existing_type.to_dict()}), 200

    new_meal_type = add_meal_type(**data)
    if new_meal_type:
        return jsonify({"message": "餐食类型添加成功", "meal_type": new_meal_type.to_dict()}), 201
    return jsonify({"error": "餐食类型添加失败"}), 500

@meal_type_bp.route('/<int:type_id>', methods=['GET'])
def api_get_meal_type(type_id):
    meal_type = get_meal_type_by_id(type_id)
    if meal_type:
        return jsonify({"message": "餐食类型获取成功", "meal_type": meal_type.to_dict()}), 200
    return jsonify({"error": "餐食类型未找到"}), 404

@meal_type_bp.route('/name/<string:type_name>', methods=['GET'])
def api_get_meal_type_by_name(type_name):
    meal_type = get_meal_type_by_name(type_name)
    if meal_type:
        return jsonify({"message": "餐食类型获取成功", "meal_type": meal_type.to_dict()}), 200
    return jsonify({"error": "餐食类型未找到"}), 404

@meal_type_bp.route('/', methods=['GET'])
def api_get_all_meal_types():
    meal_types = get_all_meal_types()
    return jsonify({"message": "所有餐食类型获取成功", "meal_types": [mt.to_dict() for mt in meal_types]}), 200

# --- 新增 API 路由：根据时间描述查询餐食类型 ---
@meal_type_bp.route('/by_time/<string:time_string>', methods=['GET'])
def api_get_meal_types_by_time(time_string):
    """
    根据 description 字段中包含的时间字符串获取餐食类型。
    URL: /meal_types/by_time/<time_string>
    Example: /meal_types/by_time/8:00
    """
    meal_types = get_meal_types_by_time_description(time_string)
    if meal_types:
        return jsonify({"message": f"成功获取包含时间 '{time_string}' 的餐食类型", "meal_types": [mt.to_dict() for mt in meal_types]}), 200
    return jsonify({"message": f"未找到包含时间 '{time_string}' 的餐食类型"}), 404


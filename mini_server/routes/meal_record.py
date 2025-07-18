# meal_record_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from mini_server.service.meal_record_service import (
    add_meal_record, get_meal_record_by_id, get_daily_meal_records,
    get_today_meal_records, get_meal_nutrition_summary, get_daily_nutrition_summary,
    update_meal_record, delete_meal_record, get_records_by_openid_date_and_type,generate_meal_detail
)

record_bp = Blueprint('records', __name__, url_prefix='/records')

@record_bp.route('', methods=['POST'])
def create_record():
    data = request.get_json()
    data.pop('name', None)
    print("================================data====")
    print(data)
    record = add_meal_record(**data)
    return jsonify({"code":200,"message": "添加成功", "record": record.to_dict()}), 200 if record else 400

@record_bp.route('/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = get_meal_record_by_id(record_id)
    return jsonify(record.to_dict()) if record else ('', 404)

@record_bp.route('/daily/<string:openid>/<string:date_str>', methods=['GET'])
def get_daily_records(openid, date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    records = get_daily_meal_records(openid, date)
    return jsonify([r.to_dict() for r in records])

@record_bp.route('/today/<string:openid>', methods=['GET'])
def get_today_records(openid):
    records = get_today_meal_records(openid)
    return jsonify([r.to_dict() for r in records])



@record_bp.route('/summary/<string:openid>/<string:date_str>/<int:meal_type_id>', methods=['GET'])
def get_nutrition_summary(openid, date_str, meal_type_id):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    summary = get_meal_nutrition_summary(openid, date, meal_type_id)
    return jsonify(summary)

@record_bp.route('/daily_summary/<string:openid>/<string:date_str>', methods=['GET'])
def get_daily_nutrition_summary_route(openid, date_str):
    """获取用户某天所有餐食的营养汇总"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    summary = get_daily_nutrition_summary(openid, date_obj)
    return jsonify(summary)

@record_bp.route('/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.get_json()
    updated = update_meal_record(record_id, **data)
    return jsonify(updated.to_dict()) if updated else ('', 404)

@record_bp.route('/<int:record_id>', methods=['DELETE'])
def remove_record(record_id):
    success = delete_meal_record(record_id)
    return '', 204 if success else 404

@record_bp.route('/meal-detail/<string:openid>/<int:meal_type_id>', methods=['GET'])
def get_meal_detail_route(openid, meal_type_id):
    meal_date_str = request.args.get('date')  # 格式: YYYY-MM-DD
    meal_date = None

    if meal_date_str:
        try:
            meal_date = datetime.strptime(meal_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                "code": 400,
                "message": "日期格式错误，请使用 YYYY-MM-DD"
            }), 400

    meal_detail = generate_meal_detail(openid, meal_type_id, meal_date)

    if not meal_detail:
        return jsonify({
            "code": 404,
            "message": "未找到相关餐食记录",
            "data": None
        }), 404

    return jsonify({
        "code": 200,
        "message": "获取餐食详情成功",
        "data": meal_detail
    })


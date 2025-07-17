# meal_record_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from service.meal_record_service import (
    add_meal_record, get_meal_record_by_id, get_daily_meal_records,
    get_today_meal_records, get_meal_nutrition_summary,get_daily_nutrition_summary,
    update_meal_record, delete_meal_record
)

record_bp = Blueprint('records', __name__, url_prefix='/records')

@record_bp.route('', methods=['POST'])
def create_record():
    data = request.get_json()
    record = add_meal_record(**data)
    return jsonify(record.to_dict()), 201 if record else 400

@record_bp.route('/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = get_meal_record_by_id(record_id)
    return jsonify(record.to_dict()) if record else ('', 404)

@record_bp.route('/daily/<string:openid>/<string:date_str>', methods=['GET'])
def get_daily_records(openid, date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    records = get_daily_meal_records(openid, date)
    return jsonify([r.to_dict() for r in records])

@record_bp.route('/score/<string:openid>/<string:date_str>', methods=['GET'])
def get_score_records(openid, date_str):
    return jsonify({"energy_kcal":0.5, "carbohydrates":0.6, "protein":0.9, "fat":1})

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
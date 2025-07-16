# api/meal_record_routes.py
from flask import Blueprint, jsonify, request
from app.services.meal_record_service import(
    add_meal_record,
    get_meal_record_by_id,
    update_meal_record,
    delete_meal_record,
    get_meal_records_by_user_openid,
    get_meal_records_by_user_and_date,
    get_meal_records_by_user_and_meal_type,
    get_all_meal_records,
    get_daily_summary_for_user
)
import logging

logger = logging.getLogger(__name__)

meal_record_bp = Blueprint('meal_record_bp', __name__, url_prefix='/meal_records')

@meal_record_bp.route('/', methods=['POST'])
def api_add_meal_record():
    data = request.json
    required_fields = ['user_openid', 'food_id', 'meal_type_id', 'amount', 'meal_date']
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"缺少必要字段: {', '.join(required_fields)}"}), 400

    # 将所有kwargs直接传递给服务层，服务层处理类型转换和计算
    new_record = add_meal_record(**data)
    if new_record:
        return jsonify({"message": "饮食记录添加成功", "record": new_record.to_dict()}), 201
    return jsonify({"error": "饮食记录添加失败"}), 500

@meal_record_bp.route('/<int:record_id>', methods=['GET'])
def api_get_meal_record(record_id):
    record = get_meal_record_by_id(record_id)
    if record:
        return jsonify({"message": "饮食记录获取成功", "record": record.to_dict()}), 200
    return jsonify({"error": f"饮食记录 ID: {record_id} 未找到"}), 404

@meal_record_bp.route('/<int:record_id>', methods=['PUT'])
def api_update_meal_record(record_id):
    data = request.json
    if not data:
        return jsonify({"error": "请求体为空"}), 400
    updated_record = update_meal_record(record_id, **data)
    if updated_record:
        return jsonify({"message": "饮食记录更新成功", "record": updated_record.to_dict()}), 200
    return jsonify({"error": "饮食记录更新失败或记录不存在"}), 404

@meal_record_bp.route('/<int:record_id>', methods=['DELETE'])
def api_delete_meal_record(record_id):
    if delete_meal_record(record_id):
        return jsonify({"message": f"饮食记录 ID: {record_id} 删除成功"}), 200
    return jsonify({"error": "饮食记录删除失败或记录不存在"}), 404

# --- 查询接口 ---
@meal_record_bp.route('/user/<string:user_openid>', methods=['GET'])
def api_get_meal_records_by_user(user_openid):
    records = get_meal_records_by_user_openid(user_openid)
    return jsonify({"message": f"用户 {user_openid} 的饮食记录获取成功", "records": [r.to_dict() for r in records]}), 200

@meal_record_bp.route('/user/<string:user_openid>/date/<string:meal_date>', methods=['GET'])
def api_get_meal_records_by_user_and_date_route(user_openid, meal_date):
    records = get_meal_records_by_user_and_date(user_openid, meal_date)
    if records is not None: # records will be empty list or actual records, or None if date format is bad
        return jsonify({"message": f"用户 {user_openid} 在 {meal_date} 的饮食记录获取成功", "records": [r.to_dict() for r in records]}), 200
    return jsonify({"error": f"日期格式不正确或获取失败: {meal_date}. 请使用 YYYY-MM-DD 格式."}), 400

@meal_record_bp.route('/user/<string:user_openid>/meal_type/<int:meal_type_id>', methods=['GET'])
def api_get_meal_records_by_user_and_meal_type_route(user_openid, meal_type_id):
    records = get_meal_records_by_user_and_meal_type(user_openid, meal_type_id)
    return jsonify({"message": f"用户 {user_openid} 在餐食类型 {meal_type_id} 的饮食记录获取成功", "records": [r.to_dict() for r in records]}), 200

@meal_record_bp.route('/all', methods=['GET'])
def api_get_all_meal_records():
    # 注意：这个接口可能返回大量数据，生产环境中应谨慎使用或添加分页
    records = get_all_meal_records()
    return jsonify({"message": "所有饮食记录获取成功", "records": [r.to_dict() for r in records]}), 200

@meal_record_bp.route('/user/<string:user_openid>/daily_summary/<string:meal_date>', methods=['GET'])
def api_get_daily_summary(user_openid, meal_date):
    summary = get_daily_summary_for_user(user_openid, meal_date)
    if summary:
        return jsonify({"message": f"用户 {user_openid} 在 {meal_date} 的每日汇总获取成功", "summary": summary}), 200
    return jsonify({"message": f"用户 {user_openid} 在 {meal_date} 没有饮食记录或汇总失败"}), 404

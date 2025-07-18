import json
from datetime import datetime

from flask import Blueprint, request, jsonify

from mini_server.util.api import upload_json_file, run_workflow_and_extract
from mini_server.vo.user_daily_info import PersonalInfo, FoodItem, DailyGoals, DailyIntake, DailyInfo, ComplexEncoder

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')


@analysis_bp.route('', methods=['GET'])
def analysis():
    personal = PersonalInfo(68, 175, 30, 'male', ['low-carb', 'high-protein'], ['peanuts', 'shellfish'],
                            ['hypertension'], 'moderate')
    food_item = FoodItem("onion", 150, 27, 5.85, 0.3, 1.35)
    daily_goals = DailyGoals(2200, 250, 70, 150)
    daily_intake = DailyIntake(980, 105, 32, 65)
    daily_info = DailyInfo(personal, food_item, datetime.now(), 'lunch', daily_goals, daily_intake)

    user = "difyuser"

    file_id = upload_json_file(daily_info, user)
    if file_id:
        doctor, food = run_workflow_and_extract(file_id, user)
        print("\n=== DOCTOR ===\n", doctor)
        print("\n=== FOOD ===\n", food)
        return jsonify({"data": {"doctor": doctor, "food": food}, "code": 200})

    return jsonify({"code": 400, "message": "分析出错"})


@analysis_bp.route('/test', methods=['GET'])
def test():
    return jsonify({"code": 200, "message": "分析成功"})
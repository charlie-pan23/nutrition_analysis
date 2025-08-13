import json
from datetime import datetime

from flask import Blueprint, request, jsonify

from mini_server.service.food_service import get_food_by_name
from mini_server.service.meal_record_service import get_daily_nutrition_summary
from mini_server.service.meal_type_service import get_current_meal_type, get_name_by_time
from mini_server.service.user_service import get_user_by_openid
from mini_server.util.api import upload_json_file, run_workflow_and_extract
from mini_server.vo.user_daily_info import PersonalInfo, FoodItem, DailyGoals, DailyIntake, DailyInfo, ComplexEncoder

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')
from mini_server.cache_manager import global_cache as cache
@analysis_bp.route('/daily_info', methods=['GET'])
def get_daily_info():
    openid = "oJ2D36yAHQ1-RsKpSEH8Sf01HZwA"
    user = get_user_by_openid(openid)

    personal = PersonalInfo(user.height, user.weight, user.age, 'male', ['low-carb', 'high-protein'],
                            ['peanuts', 'shellfish'],
                            ['hypertension'], 'moderate')

    detections = cache.get('detections')
    weight = cache.get('weight')

    if not detections:
        return jsonify({"code": 400, "msg": "暂无数据"})

    class_name = detections[0]["class_name"]
    if not class_name:
        return jsonify({"code": 400, "msg": "识别出错"})

    food = get_food_by_name(class_name)

    food_item = FoodItem(food.name, weight, food.calories, food.carbs, food.fat, food.protein)
    daily_goals = DailyGoals(user.daily_energy_kcal, user.daily_carbohydrates_g, user.daily_fat_g, user.daily_protein_g)

    summary = get_daily_nutrition_summary(openid, datetime.now().strftime("%Y-%m-%d"))

    daily_intake = DailyIntake(summary['total_calories'], summary['total_carbs'], summary['total_fat'], summary['total_protein'])

    meal_type = get_name_by_time(get_current_meal_type())

    daily_info = DailyInfo(personal, food_item, datetime.now(), meal_type['name'], daily_goals, daily_intake)

    print(daily_info)
    return jsonify(json.dumps(daily_info, cls=ComplexEncoder, indent=2))

@analysis_bp.route('', methods=['GET'])
def analysis():
    openid = "oJ2D36yAHQ1-RsKpSEH8Sf01HZwA"
    user = get_user_by_openid(openid)

    personal = PersonalInfo(user.height, user.weight, user.age, 'male', ['low-carb', 'high-protein'], ['peanuts', 'shellfish'],
                            ['hypertension'], 'moderate')

    detections = cache.get('detections')
    weight = cache.get('weight')
    print("=========================111111=")
    print(detections)

    if not detections:
        return jsonify({"code": 400, "msg": "暂无数据"})

    class_name = detections[0]["class_name"]
    if not class_name:
        return jsonify({"code": 400, "msg": "识别出错"})

    food = get_food_by_name(class_name)

    food_item = FoodItem(food.name, weight, food.calories, food.carbs, food.fat, food.protein)
    daily_goals = DailyGoals(user.daily_energy_kcal, user.daily_carbohydrates_g, user.daily_fat_g, user.daily_protein_g)

    summary =  get_daily_nutrition_summary(openid, datetime.now().strftime("%Y-%m-%d"))

    daily_intake = DailyIntake(summary['total_calories'], summary['total_carbs'], summary['total_fat'], summary['total_protein'])

    meal_type = get_name_by_time(get_current_meal_type())

    daily_info = DailyInfo(personal, food_item, datetime.now(), meal_type['name'], daily_goals, daily_intake)

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
import json
from datetime import datetime, timezone, timedelta


class PersonalInfo:
    def __init__(self, height_cm, weight_kg,
                 age, gender, preferences, allergies, chronic_conditions, activity_level):
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.age = age
        self.gender = gender
        self.preferences = preferences
        self.allergies = allergies
        self.chronic_conditions = chronic_conditions
        self.activity_level = activity_level



class FoodItem:
    def __init__(self, name, weight_g, energy_kcal, carbohydrates_g, fat_g, protein_g):
        self.name = name
        self.weight_g = weight_g
        self.energy_kcal = energy_kcal
        self.carbohydrates_g = carbohydrates_g
        self.fat_g = fat_g
        self.protein_g = protein_g


class DailyGoals:
    def __init__(self, energy_kcal, carbohydrates_g, fat_g, protein_g):
        self.energy_kcal = energy_kcal
        self.carbohydrates_g = carbohydrates_g
        self.fat_g = fat_g
        self.protein_g = protein_g


class DailyIntake:
    def __init__(self, energy_kcal, carbohydrates_g, fat_g, protein_g):
        self.energy_kcal = energy_kcal
        self.carbohydrates_g = carbohydrates_g
        self.fat_g = fat_g
        self.protein_g = protein_g


class DailyInfo:
    def __init__(self, personal_info, food_item, current_time,
                 meal_type, daily_goals, daily_intake):
        self.personal_info = personal_info
        self.food_item = food_item
        self.current_time = current_time
        self.meal_type = meal_type
        self.daily_goals = daily_goals
        self.daily_intake = daily_intake

class DailyInfo1:
    def __init__(self, personal_info):
        self.personal_info = personal_info


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return format_time(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

def format_time(datetime_obj):
    tz = timezone(timedelta(hours=8))  # 设置为 UTC+8
    now = datetime.now(tz)

    # 转换为目标格式（不带毫秒）
    formatted_time = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    formatted_time = formatted_time[:-2] + ":" + formatted_time[-2:]  # 将 +0800 → +08:00
    return formatted_time





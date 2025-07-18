from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from base import engine
from models.Meal_type import MealType
from datetime import datetime, time, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

def _parse_time(time_str):
    """将时间字符串转换为 time 对象"""
    if not time_str:
        return None
    return datetime.strptime(time_str, "%H:%M:%S").time()


def get_name_by_id(meal_type_id):
    """
    通过ID获取餐食类型名称
    :param meal_type_id: 餐食类型ID
    :return: 餐食类型名称或None
    """
    try:
        meal_type = session.query(MealType).get(meal_type_id)
        return meal_type.name if meal_type else None
    except SQLAlchemyError as e:
        logger.error(f"通过ID获取名称失败: {e}")
        return None


def get_id_by_name(name):
    """
    通过名称获取餐食类型ID
    :param name: 餐食类型名称
    :return: 餐食类型ID或None
    """
    try:
        meal_type = session.query(MealType).filter(MealType.name == name).first()
        return meal_type.id if meal_type else None
    except SQLAlchemyError as e:
        logger.error(f"通过名称获取ID失败: {e}")
        return None


def get_name_by_time(target_time_str):
    """
    通过具体时间获取餐食类型名称和ID
    :param target_time_str: 时间字符串，格式为"HH:MM:SS"
    :return: 包含餐食类型名称和ID的字典，如 {"name": "早餐", "id": 1} 或 None
    """
    try:
        # 将字符串转换为时间对象
        target_time = _parse_time(target_time_str)
        if not target_time:
            return {"name": "加餐", "id": 5}

        # 处理夜宵的特殊情况（跨天）
        meal_types = session.query(MealType).filter(MealType.id != 5).all()

        for mt in meal_types:
            if mt.id == 4:  # 夜宵
                # 处理跨天情况
                if (target_time >= mt.start_time) or (target_time <= mt.end_time):
                    return {"name": mt.name, "id": mt.id}
            elif mt.start_time and mt.end_time and (mt.start_time <= target_time <= mt.end_time):
                return {"name": mt.name, "id": mt.id}

        return {"name": "加餐", "id": 5}
    except Exception as e:
        logger.error(f"通过时间获取名称失败: {e}")
        return None



def get_current_meal_type():
    """
    通过当前时间获取餐食类型名称
    :return: 餐食类型名称
    """
    return get_name_by_time(datetime.now().strftime("%H:%M:%S"))

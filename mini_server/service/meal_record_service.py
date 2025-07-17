from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from base import engine
from models.Meal_record import MealRecord
from models.User import User
from service.food_service import get_food_by_id

import logging

from service.user_service import get_user_by_openid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_
from sqlalchemy.orm import sessionmaker

from base import engine
from models.Meal_record import MealRecord
from service.food_service import get_food_by_id

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()


def add_meal_record(**kwargs):
    """
    添加新的餐食记录
    :param kwargs: 包含餐食记录数据的字典
    :return: MealRecord对象或None
    """
    try:
        # 计算实际摄入的营养素
        food_id = kwargs.get('food_id')
        amount = kwargs.get('amount', 100.0)

        if food_id and amount:
            food = get_food_by_id(food_id)
            if food:
                # 根据食物营养成分和摄入量计算实际摄入量
                ratio = amount / 100.0
                kwargs['calories'] = food.calories * ratio
                kwargs['protein'] = food.protein_g * ratio
                kwargs['fat'] = food.fat_g * ratio
                kwargs['carbs'] = food.carbohydrates_g * ratio
                kwargs['fiber'] = food.fiber_g * ratio

        new_record = MealRecord(**kwargs)
        session.add(new_record)
        session.commit()
        logger.info(f"添加餐食记录成功，ID: {new_record.id}")
        return new_record
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"添加餐食记录失败: {e}", exc_info=True)
        return None


def get_meal_record_by_id(record_id):
    """
    根据ID获取餐食记录
    :param record_id: 餐食记录ID
    :return: MealRecord对象或None
    """
    try:
        record = session.query(MealRecord).get(record_id)
        if record:
            logger.info(f"获取餐食记录成功，ID: {record_id}")
            return record
        logger.warning(f"餐食记录ID: {record_id} 未找到")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取餐食记录失败: {e}", exc_info=True)
        return None


def get_daily_meal_records(openid, meal_date):
    """
    获取用户某天的所有餐食记录
    :param openid: 用户OpenID
    :param meal_date: 用餐日期 (datetime.date对象)
    :return: MealRecord对象列表
    """
    try:
        records = session.query(MealRecord).filter(
            MealRecord.user_openid == openid,
            MealRecord.meal_date == meal_date
        ).order_by(MealRecord.meal_time).all()

        logger.info(f"获取用户{openid}在{meal_date}的餐食记录，共{len(records)}条")
        return records
    except SQLAlchemyError as e:
        logger.error(f"获取餐食记录失败: {e}", exc_info=True)
        return []


def get_today_meal_records(openid):
    """
    获取用户今天的餐食记录
    :param openid: 用户OpenID
    :return: MealRecord对象列表
    """
    today = date.today()
    return get_daily_meal_records(openid, today)


def get_meal_nutrition_summary(openid, meal_date, meal_type_id):
    """
    获取用户某天某餐的营养摄入汇总
    :param openid: 用户OpenID
    :param meal_date: 用餐日期 (datetime.date对象)
    :param meal_type_id: 餐食类型ID
    :return: 营养汇总字典
    """
    try:
        result = session.query(
            func.sum(MealRecord.calories).label('total_calories'),
            func.sum(MealRecord.protein).label('total_protein'),
            func.sum(MealRecord.fat).label('total_fat'),
            func.sum(MealRecord.carbs).label('total_carbs'),
            func.sum(MealRecord.fiber).label('total_fiber')
        ).filter(
            MealRecord.user_openid == openid,
            MealRecord.meal_date == meal_date,
            MealRecord.meal_type_id == meal_type_id
        ).first()

        if result:
            summary = {
                'total_calories': float(result.total_calories) if result.total_calories else 0.0,
                'total_protein': float(result.total_protein) if result.total_protein else 0.0,
                'total_fat': float(result.total_fat) if result.total_fat else 0.0,
                'total_carbs': float(result.total_carbs) if result.total_carbs else 0.0,
                'total_fiber': float(result.total_fiber) if result.total_fiber else 0.0
            }
            logger.info(f"获取用户{openid}在{meal_date}的{meal_type_id}餐营养汇总成功")
            return summary

        logger.info(f"用户{openid}在{meal_date}没有{meal_type_id}餐的记录")
        return {
            'total_calories': 0.0,
            'total_protein': 0.0,
            'total_fat': 0.0,
            'total_carbs': 0.0,
            'total_fiber': 0.0
        }
    except SQLAlchemyError as e:
        logger.error(f"获取营养汇总失败: {e}", exc_info=True)
        return {
            'total_calories': 0.0,
            'total_protein': 0.0,
            'total_fat': 0.0,
            'total_carbs': 0.0,
            'total_fiber': 0.0
        }
def get_daily_nutrition_summary(openid, meal_date):
    """
    获取用户某天所有餐食的营养摄入汇总
    :param openid: 用户OpenID
    :param meal_date: 用餐日期 (datetime.date对象)
    :return: 营养汇总字典
    """
    try:
        user =  get_user_by_openid(openid)

        result = session.query(
            func.sum(MealRecord.calories).label('total_calories'),
            func.sum(MealRecord.protein).label('total_protein'),
            func.sum(MealRecord.fat).label('total_fat'),
            func.sum(MealRecord.carbs).label('total_carbs'),
            func.sum(MealRecord.fiber).label('total_fiber')
        ).filter(
            MealRecord.user_openid == openid,
            MealRecord.meal_date == meal_date
        ).first()

        if result:
            summary = {
                'total_calories': round(float(
                    result.total_calories) / user.daily_energy_kcal,2) if result.total_calories else 0.0,
                'total_protein': round(float(result.total_protein) / user.daily_protein_g,2) if result.total_protein else 0.0,
                'total_fat': round(float(result.total_fat) / user.daily_fat_g,2) if result.total_fat else 0.0,
                'total_carbs': round(float(result.total_carbs) / user.daily_carbohydrates_g,2) if result.total_carbs else 0.0,
                'total_fiber': float(result.total_fiber) if result.total_fiber else 0.0
            }
            logger.info(f"获取用户{openid}在{meal_date}的每日营养汇总成功")
            return summary

        logger.info(f"用户{openid}在{meal_date}没有餐食记录")
        return {
            'total_calories': 0.0,
            'total_protein': 0.0,
            'total_fat': 0.0,
            'total_carbs': 0.0,
            'total_fiber': 0.0
        }
    except SQLAlchemyError as e:
        logger.error(f"获取每日营养汇总失败: {e}", exc_info=True)
        return {
            'total_calories': 0.0,
            'total_protein': 0.0,
            'total_fat': 0.0,
            'total_carbs': 0.0,
            'total_fiber': 0.0
        }

def update_meal_record(record_id, **kwargs):
    """
    更新餐食记录
    :param record_id: 记录ID
    :param kwargs: 要更新的字段
    :return: 更新后的MealRecord对象或None
    """
    try:
        record = session.query(MealRecord).get(record_id)
        if not record:
            logger.warning(f"更新失败: 记录ID {record_id} 不存在")
            return None

        # 如果需要重新计算营养值
        if 'food_id' in kwargs or 'amount' in kwargs:
            food_id = kwargs.get('food_id', record.food_id)
            amount = kwargs.get('amount', record.amount)

            food = get_food_by_id(food_id)
            if food:
                ratio = amount / 100.0
                kwargs['calories'] = food.calories * ratio
                kwargs['protein'] = food.protein_g * ratio
                kwargs['fat'] = food.fat_g * ratio
                kwargs['carbs'] = food.carbohydrates_g * ratio
                kwargs['fiber'] = food.fiber_g * ratio

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(record, key) and key not in ['id', 'created_at']:
                setattr(record, key, value)

        session.commit()
        logger.info(f"更新餐食记录成功，ID: {record_id}")
        return record
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"更新餐食记录失败: {e}", exc_info=True)
        return None


def delete_meal_record(record_id):
    """
    删除餐食记录
    :param record_id: 记录ID
    :return: 是否删除成功
    """
    try:
        record = session.query(MealRecord).get(record_id)
        if record:
            session.delete(record)
            session.commit()
            logger.info(f"删除餐食记录成功，ID: {record_id}")
            return True
        logger.warning(f"删除失败: 记录ID {record_id} 不存在")
        return False
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"删除餐食记录失败: {e}", exc_info=True)
        return False
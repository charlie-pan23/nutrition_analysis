from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from base import engine
from models.Food import Food

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()


# --- 2. 数据库操作函数 (CRUD Operations for Food) ---

def add_food(**kwargs):
    """
    向数据库添加一个新食物。
    :param kwargs: 包含食物数据的字典，如 name, calories 等。
    :return: Food 对象如果成功，否则返回 None。
    """
    try:
        new_food = Food(**kwargs)
        session.add(new_food)
        session.commit()
        logger.info(f"食物 '{new_food.name}' 添加成功。")
        return new_food
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"添加食物失败: {e}", exc_info=True)
        return None

def get_food_by_id(food_id):
    """
    根据 ID 获取单个食物。
    :param food_id: 食物的唯一标识符 (主键)。
    :return: Food 对象如果找到，否则返回 None。
    """
    try:
        food = session.query(Food).get(food_id) # 使用 .get() 通过主键查询更高效
        # food = session.query(Food).filter(Food.id == food_id).first()
        if food:
            logger.info(f"成功获取食物 ID: {food_id}。")
            return food
        logger.info(f"食物 ID: {food_id} 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取食物 ID: {food_id} 失败: {e}", exc_info=True)
        return None

def get_food_by_name(food_name):
    """
    根据食物名称获取单个食物。
    :param food_name: 食物的名称。
    :return: Food 对象如果找到，否则返回 None。
    """
    try:

        food = session.query(Food).filter(Food.name == food_name).first()
        if food:
            logger.info(f"成功获取食物 '{food_name}'。")
            return food
        logger.info(f"食物 '{food_name}' 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取食物 '{food_name}' 失败: {e}", exc_info=True)
        return None

def get_all_foods():
    """
    获取所有食物。
    :return: Food 对象列表。
    """
    try:
        foods = session.query(Food).all()
        logger.info(f"成功获取所有食物列表，共 {len(foods)} 条。")
        return foods
    except SQLAlchemyError as e:
        logger.error(f"获取所有食物失败: {e}", exc_info=True)
        return []

def update_food(food_id, **kwargs):
    """
    更新食物信息。
    :param food_id: 食物的唯一标识符。
    :param kwargs: 要更新的字段及其新值的字典。
    :return: 更新后的 Food 对象如果成功，否则返回 None。
    """
    try:
        food = session.query(Food).get(food_id)
        if food:
            for key, value in kwargs.items():
                # 检查属性是否存在，避免设置不存在的字段
                if hasattr(food, key) and key not in ['id', 'created_at']: # id 和 created_at 通常不更新
                    setattr(food, key, value)
            session.commit()
            logger.info(f"食物 ID: {food_id} 更新成功。")
            return food
        logger.warning(f"尝试更新食物 ID: {food_id} 失败：食物不存在。")
        return None
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"更新食物 ID: {food_id} 失败: {e}", exc_info=True)
        return None

def delete_food(food_id):
    """
    从数据库中删除一个食物。
    :param food_id: 食物的唯一标识符。
    :return: True 如果删除成功，False 如果失败或食物不存在。
    """
    try:
        food = session.query(Food).get(food_id)
        if food:
            session.delete(food)
            session.commit()
            logger.info(f"食物 ID: {food_id} 删除成功。")
            return True
        logger.warning(f"尝试删除食物 ID: {food_id} 失败：食物不存在。")
        return False
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"删除食物 ID: {food_id} 失败: {e}", exc_info=True)
        return False

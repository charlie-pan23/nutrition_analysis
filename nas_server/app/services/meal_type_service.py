# meal_type_service.py
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. 定义数据模型 (MealType Model) ---
class MealType(db.Model):
    __tablename__ = 'meal_types'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False) # 与数据库表的 varchar(20) 对应
    description = db.Column(db.String(100), nullable=True) # 与数据库表的 varchar(100) 对应，可空

    def __repr__(self):
        return f'<MealType {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# --- 2. 数据库操作函数 (基础 CRUD for MealType) ---
def add_meal_type(**kwargs):
    """添加一个新的餐食类型。"""
    try:
        new_meal_type = MealType(**kwargs)
        db.session.add(new_meal_type)
        db.session.commit()
        logger.info(f"餐食类型 '{new_meal_type.name}' 添加成功。")
        return new_meal_type
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"添加餐食类型失败: {e}", exc_info=True)
        return None

def get_meal_type_by_id(meal_type_id):
    """根据 ID 获取餐食类型。"""
    try:
        meal_type = MealType.query.get(meal_type_id)
        if meal_type:
            logger.info(f"成功获取餐食类型 ID: {meal_type_id}。")
            return meal_type
        logger.info(f"餐食类型 ID: {meal_type_id} 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取餐食类型 ID: {meal_type_id} 失败: {e}", exc_info=True)
        return None

def get_meal_type_by_name(meal_type_name):
    """根据名称获取餐食类型。"""
    try:
        meal_type = MealType.query.filter_by(name=meal_type_name).first()
        if meal_type:
            logger.info(f"成功获取餐食类型 '{meal_type_name}'。")
            return meal_type
        logger.info(f"餐食类型 '{meal_type_name}' 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取餐食类型 '{meal_type_name}' 失败: {e}", exc_info=True)
        return None

def get_all_meal_types():
    """获取所有餐食类型。"""
    try:
        meal_types = MealType.query.all()
        logger.info(f"成功获取所有餐食类型，共 {len(meal_types)} 条。")
        return meal_types
    except SQLAlchemyError as e:
        logger.error(f"获取所有餐食类型失败: {e}", exc_info=True)
        return []

# --- 新增查询函数 ---
def get_meal_types_by_time_description(time_string):
    """
    根据 description 字段中包含的时间字符串查询餐食类型。
    例如：time_string = "8:00" 可以匹配 "8:00-9:00" 或 "7:30-8:30"
    :param time_string: 要匹配的时间字符串，例如 "8:00"
    :return: MealType 对象列表。
    """
    try:
        # 使用 SQLAlchemy 的 like 方法进行模糊匹配
        # '%{}%'.format(time_string) 会生成类似 '%8:00%' 的字符串
        meal_types = MealType.query.filter(MealType.description.like(f'%{time_string}%')).all()
        logger.info(f"成功获取包含时间 '{time_string}' 的餐食类型，共 {len(meal_types)} 条。")
        return meal_types
    except SQLAlchemyError as e:
        logger.error(f"根据时间描述查询餐食类型失败: {e}", exc_info=True)
        return []

# meal_record_service.py
from datetime import datetime, date, time
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func # 导入 func 用于聚合函数
import logging

# 导入相关服务层的模型，用于外键关联和数据查询
from app.services.user_service import User
from app.services.food_service import Food, get_food_by_id # 需要 get_food_by_id 来获取食物营养数据
from app.services.meal_type_service import MealType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. 定义数据模型 (MealRecord Model) ---
class MealRecord(db.Model):
    __tablename__ = 'meal_records'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_openid = db.Column(db.String(100), db.ForeignKey('users.openid', ondelete='CASCADE'), nullable=False, comment='用户openid')
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id', ondelete='CASCADE'), nullable=False, comment='食物ID')
    meal_type_id = db.Column(db.Integer, db.ForeignKey('meal_types.id'), nullable=False, comment='餐食类型ID')
    amount = db.Column(db.Numeric(8, 2), default=100.00, nullable=False, comment='食用量(g)')
    unit = db.Column(db.String(20), default='g', comment='单位')
    calories = db.Column(db.Numeric(8, 2), default=0.00, comment='实际摄入热量(kcal)')
    carbs = db.Column(db.Numeric(8, 2), default=0.00, comment='实际摄入碳水化合物(g)')
    fat = db.Column(db.Numeric(8, 2), default=0.00, comment='实际摄入脂肪(g)')
    protein = db.Column(db.Numeric(8, 2), default=0.00, comment='实际摄入蛋白质(g)')
    fiber = db.Column(db.Numeric(8, 2), default=0.00, comment='实际摄入膳食纤维(g)')
    meal_date = db.Column(db.Date, nullable=False, comment='用餐日期')
    meal_time = db.Column(db.Time, comment='用餐时间')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 定义关系
    user = db.relationship('User', backref=db.backref('meal_records', lazy=True))
    food = db.relationship('Food', backref=db.backref('meal_records', lazy=True))
    meal_type = db.relationship('MealType', backref=db.backref('meal_records', lazy=True))

    def __repr__(self):
        return f'<MealRecord {self.id} User:{self.user_openid} Food:{self.food_id} Date:{self.meal_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_openid': self.user_openid,
            'food_id': self.food_id,
            'meal_type_id': self.meal_type_id,
            'amount': float(self.amount), # 转换为 float 以便 JSON 序列化
            'unit': self.unit,
            'calories': float(self.calories),
            'carbs': float(self.carbs),
            'fat': float(self.fat),
            'protein': float(self.protein),
            'fiber': float(self.fiber),
            'meal_date': self.meal_date.isoformat() if self.meal_date else None,
            'meal_time': self.meal_time.isoformat() if self.meal_time else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'food_name': self.food.name if self.food else None, # 关联食物名称
            'meal_type_name': self.meal_type.name if self.meal_type else None # 关联餐食类型名称
        }

# --- 2. 辅助函数：计算营养成分 ---
def _calculate_nutrients(food_id, amount):
    """
    根据食物ID和食用量计算实际摄入的营养成分。
    假设 Food 模型中的营养成分是每 100g 的量。
    """
    food = get_food_by_id(food_id)
    if not food:
        logger.warning(f"计算营养成分失败：食物 ID {food_id} 未找到。")
        return {
            'calories': 0.0, 'carbs': 0.0, 'fat': 0.0,
            'protein': 0.0, 'fiber': 0.0
        }

    # 转换为每克营养成分
    factor = float(amount) / 100.0 if amount else 0.0

    return {
        'calories': round(food.calories * factor, 2),
        'carbs': round(food.carbohydrates_g * factor, 2),
        'fat': round(food.fat_g * factor, 2),
        'protein': round(food.protein_g * factor, 2),
        'fiber': round(food.fiber_g * factor, 2)
    }

# --- 3. 数据库操作函数 (CRUD Operations for MealRecord) ---

def add_meal_record(user_openid, food_id, meal_type_id, amount, meal_date, meal_time=None, notes=None, unit='g'):
    """
    添加一个新的饮食记录，并自动计算营养成分。
    :param user_openid: 用户 OpenID
    :param food_id: 食物 ID
    :param meal_type_id: 餐食类型 ID
    :param amount: 食用量 (g)
    :param meal_date: 用餐日期 (datetime.date 或 'YYYY-MM-DD' 字符串)
    :param meal_time: 用餐时间 (datetime.time 或 'HH:MM:SS' 字符串, 可选)
    :param notes: 备注 (可选)
    :param unit: 单位 (默认为 'g')
    :return: MealRecord 对象如果成功，否则返回 None。
    """
    try:
        # 类型转换
        if isinstance(meal_date, str):
            meal_date = date.fromisoformat(meal_date)
        if isinstance(meal_time, str):
            meal_time = time.fromisoformat(meal_time)

        # 计算营养成分
        nutrients = _calculate_nutrients(food_id, amount)

        new_record = MealRecord(
            user_openid=user_openid,
            food_id=food_id,
            meal_type_id=meal_type_id,
            amount=amount,
            unit=unit,
            calories=nutrients['calories'],
            carbs=nutrients['carbs'],
            fat=nutrients['fat'],
            protein=nutrients['protein'],
            fiber=nutrients['fiber'],
            meal_date=meal_date,
            meal_time=meal_time,
            notes=notes
        )
        db.session.add(new_record)
        db.session.commit()
        logger.info(f"饮食记录添加成功：用户 {user_openid}, 食物 {food_id}, 日期 {meal_date}。")
        return new_record
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"添加饮食记录失败: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"处理饮食记录数据失败: {e}", exc_info=True)
        return None

def get_meal_record_by_id(record_id):
    """
    根据 ID 获取单个饮食记录。
    :param record_id: 饮食记录的唯一标识符。
    :return: MealRecord 对象如果找到，否则返回 None。
    """
    try:
        # 使用 .get() 通过主键查询，并同时加载关联的 food 和 meal_type
        record = MealRecord.query.options(db.joinedload(MealRecord.food), db.joinedload(MealRecord.meal_type)).get(record_id)
        if record:
            logger.info(f"成功获取饮食记录 ID: {record_id}。")
            return record
        logger.info(f"饮食记录 ID: {record_id} 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取饮食记录 ID: {record_id} 失败: {e}", exc_info=True)
        return None

def update_meal_record(record_id, **kwargs):
    """
    更新饮食记录信息。如果更新了 amount 或 food_id，将重新计算营养成分。
    :param record_id: 饮食记录的唯一标识符。
    :param kwargs: 要更新的字段及其新值的字典。
    :return: 更新后的 MealRecord 对象如果成功，否则返回 None。
    """
    try:
        record = MealRecord.query.get(record_id)
        if record:
            recalculate_nutrients = False
            for key, value in kwargs.items():
                if hasattr(record, key) and key not in ['id', 'created_at', 'updated_at']:
                    # 处理日期和时间字符串到对象转换
                    if key == 'meal_date' and isinstance(value, str):
                        value = date.fromisoformat(value)
                    elif key == 'meal_time' and isinstance(value, str):
                        value = time.fromisoformat(value)

                    setattr(record, key, value)
                    if key in ['amount', 'food_id']: # 如果金额或食物ID改变，需要重新计算
                        recalculate_nutrients = True

            if recalculate_nutrients:
                # 重新计算并更新营养成分
                nutrients = _calculate_nutrients(record.food_id, record.amount)
                record.calories = nutrients['calories']
                record.carbs = nutrients['carbs']
                record.fat = nutrients['fat']
                record.protein = nutrients['protein']
                record.fiber = nutrients['fiber']

            db.session.commit()
            logger.info(f"饮食记录 ID: {record_id} 更新成功。")
            return record
        logger.warning(f"尝试更新饮食记录 ID: {record_id} 失败：记录不存在。")
        return None
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"更新饮食记录 ID: {record_id} 失败: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"处理饮食记录更新数据失败: {e}", exc_info=True)
        return None


def delete_meal_record(record_id):
    """
    从数据库中删除一个饮食记录。
    :param record_id: 饮食记录的唯一标识符。
    :return: True 如果删除成功，False 如果失败或记录不存在。
    """
    try:
        record = MealRecord.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
            logger.info(f"饮食记录 ID: {record_id} 删除成功。")
            return True
        logger.warning(f"尝试删除饮食记录 ID: {record_id} 失败：记录不存在。")
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"删除饮食记录 ID: {record_id} 失败: {e}", exc_info=True)
        return False

def get_meal_records_by_user_openid(user_openid):
    """
    根据用户 OpenID 获取该用户的所有饮食记录。
    :param user_openid: 用户的 OpenID。
    :return: MealRecord 对象列表。
    """
    try:
        # 同时加载关联的 food 和 meal_type，避免 N+1 查询问题
        records = MealRecord.query.options(db.joinedload(MealRecord.food), db.joinedload(MealRecord.meal_type)).filter_by(user_openid=user_openid).order_by(MealRecord.meal_date.desc(), MealRecord.meal_time.desc()).all()
        logger.info(f"成功获取用户 {user_openid} 的所有饮食记录，共 {len(records)} 条。")
        return records
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {user_openid} 的饮食记录失败: {e}", exc_info=True)
        return []

def get_meal_records_by_user_and_date(user_openid, meal_date_str):
    """
    根据用户 OpenID 和指定日期获取饮食记录。
    :param user_openid: 用户的 OpenID。
    :param meal_date_str: 用餐日期字符串 (YYYY-MM-DD)。
    :return: MealRecord 对象列表。
    """
    try:
        meal_date = date.fromisoformat(meal_date_str)
        records = MealRecord.query.options(db.joinedload(MealRecord.food), db.joinedload(MealRecord.meal_type)).filter_by(
            user_openid=user_openid,
            meal_date=meal_date
        ).order_by(MealRecord.meal_time.asc()).all()
        logger.info(f"成功获取用户 {user_openid} 在 {meal_date_str} 的饮食记录，共 {len(records)} 条。")
        return records
    except ValueError:
        logger.error(f"无效的日期格式: {meal_date_str}。请使用 YYYY-MM-DD 格式。")
        return []
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {user_openid} 在 {meal_date_str} 的饮食记录失败: {e}", exc_info=True)
        return []

def get_meal_records_by_user_and_meal_type(user_openid, meal_type_id):
    """
    根据用户 OpenID 和餐食类型获取饮食记录。
    :param user_openid: 用户的 OpenID。
    :param meal_type_id: 餐食类型 ID。
    :return: MealRecord 对象列表。
    """
    try:
        records = MealRecord.query.options(db.joinedload(MealRecord.food), db.joinedload(MealRecord.meal_type)).filter_by(
            user_openid=user_openid,
            meal_type_id=meal_type_id
        ).order_by(MealRecord.meal_date.desc(), MealRecord.meal_time.desc()).all()
        logger.info(f"成功获取用户 {user_openid} 在餐食类型 {meal_type_id} 的饮食记录，共 {len(records)} 条。")
        return records
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {user_openid} 在餐食类型 {meal_type_id} 的饮食记录失败: {e}", exc_info=True)
        return []

def get_all_meal_records():
    """获取所有饮食记录（通常只用于管理员或数据分析）。"""
    try:
        records = MealRecord.query.options(db.joinedload(MealRecord.food), db.joinedload(MealRecord.meal_type)).all()
        logger.info(f"成功获取所有饮食记录，共 {len(records)} 条。")
        return records
    except SQLAlchemyError as e:
        logger.error(f"获取所有饮食记录失败: {e}", exc_info=True)
        return []

def get_daily_summary_for_user(user_openid, meal_date_str):
    """
    获取某用户在某天的总摄入营养数据。
    """
    try:
        meal_date = date.fromisoformat(meal_date_str)
        summary = db.session.query(
            func.sum(MealRecord.calories).label('total_calories'),
            func.sum(MealRecord.carbs).label('total_carbs'),
            func.sum(MealRecord.fat).label('total_fat'),
            func.sum(MealRecord.protein).label('total_protein'),
            func.sum(MealRecord.fiber).label('total_fiber')
        ).filter(
            MealRecord.user_openid == user_openid,
            MealRecord.meal_date == meal_date
        ).first()

        if summary and summary.total_calories is not None:
            return {
                'meal_date': meal_date.isoformat(),
                'total_calories': float(summary.total_calories),
                'total_carbs': float(summary.total_carbs),
                'total_fat': float(summary.total_fat),
                'total_protein': float(summary.total_protein),
                'total_fiber': float(summary.total_fiber)
            }
        return None # 没有记录或总和为0

    except ValueError:
        logger.error(f"无效的日期格式: {meal_date_str}。请使用 YYYY-MM-DD 格式。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {user_openid} 在 {meal_date_str} 的每日汇总失败: {e}", exc_info=True)
        return None


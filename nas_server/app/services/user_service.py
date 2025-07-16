import os
from datetime import datetime
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
import logging

# 配置日志，用于记录用户相关的操作和错误
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. 定义数据模型 (User Model) ---
# User 模型继承自 db.Model，这样 SQLAlchemy 就能识别它并将其映射到数据库表
class User(db.Model):
    __tablename__ = 'users' # 定义数据库表名，通常使用小写复数形式
    __table_args__ = {'extend_existing': True}

    # 定义表的列
    id = db.Column(db.Integer, primary_key=True) # 主键，自动递增
    nickname = db.Column(db.String(80), default='New User') # 昵称，默认值
    openid = db.Column(db.String(120), unique=True, nullable=False) # 用户的唯一标识符，唯一且非空
    height = db.Column(db.Float) # 身高
    weight = db.Column(db.Float) # 体重
    age = db.Column(db.Integer)  # 年龄
    gender = db.Column(db.String(10)) # 性别
    preferences = db.Column(db.String(500)) # 饮食偏好等
    allergies = db.Column(db.String(500)) # 过敏史
    diseases = db.Column(db.String(500)) # 疾病史
    activity_level = db.Column(db.String(50), default='lightly_active') # 活动水平，默认轻度活跃
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow) # 最后登录时间，默认为当前 UTC 时间
    daily_energy_kcal = db.Column(db.Float, default=0.00) # 每日推荐能量摄入
    daily_carbohydrates_g = db.Column(db.Float, default=0.00) # 每日推荐碳水摄入
    daily_fat_g = db.Column(db.Float, default=0.00) # 每日推荐脂肪摄入
    daily_protein_g = db.Column(db.Float, default=0.00) # 每日推荐蛋白质摄入

    def __repr__(self):
        """定义对象的字符串表示，便于调试"""
        return f'<User {self.openid}>'

    def to_dict(self):
        """将 User 对象转换为字典，便于 API 响应序列化为 JSON"""
        return {
            'id': self.id,
            'nickname': self.nickname,
            'openid': self.openid,
            'height': self.height,
            'weight': self.weight,
            'age': self.age,
            'gender': self.gender,
            'preferences': self.preferences,
            'allergies': self.allergies,
            'diseases': self.diseases,
            'activity_level': self.activity_level,
            # 将 datetime 对象转换为 ISO 格式字符串，便于 JSON 序列化
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'daily_energy_kcal': self.daily_energy_kcal,
            'daily_carbohydrates_g': self.daily_carbohydrates_g,
            'daily_fat_g': self.daily_fat_g,
            'daily_protein_g': self.daily_protein_g
        }

# --- 2. 数据库操作函数 (CRUD Operations) ---
# 这些函数是 user_service 模块的公共接口，供其他模块（如 API 路由）调用

def add_user(**kwargs):
    """
    向数据库添加一个新用户。
    :param kwargs: 包含用户数据的字典，如 openid, nickname 等。
    :return: User 对象如果成功，否则返回 None。
    """
    try:
        new_user = User(**kwargs) # 使用 kwargs 直接创建 User 实例
        db.session.add(new_user) # 添加到会话
        db.session.commit()      # 提交会话，将数据写入数据库
        logger.info(f"用户 {new_user.openid} 添加成功。")
        return new_user
    except SQLAlchemyError as e:
        db.session.rollback() # 如果发生错误，回滚会话，撤销未提交的更改
        logger.error(f"添加用户失败: {e}", exc_info=True) # 记录详细错误信息
        return None

def delete_user(openid):
    """
    从数据库中删除一个用户。
    :param openid: 用户的唯一标识符。
    :return: True 如果删除成功，False 如果失败或用户不存在。
    """
    try:
        user = User.query.filter_by(openid=openid).first() # 根据 openid 查询用户
        if user:
            db.session.delete(user)  # 从会话中删除用户
            db.session.commit()      # 提交会话
            logger.info(f"用户 {openid} 删除成功。")
            return True
        logger.warning(f"尝试删除用户 {openid} 失败：用户不存在。")
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"删除用户 {openid} 失败: {e}", exc_info=True)
        return False

def update_user(openid, **kwargs):
    """
    更新用户信息。
    :param openid: 用户的唯一标识符。
    :param kwargs: 要更新的字段及其新值的字典。
    :return: 更新后的 User 对象如果成功，否则返回 None。
    """
    try:
        user = User.query.filter_by(openid=openid).first()
        if user:
            for key, value in kwargs.items():
                # 确保只更新模型中存在的属性，避免意外错误
                if hasattr(user, key):
                    setattr(user, key, value) # 使用 setattr 动态设置属性值
            db.session.commit()
            logger.info(f"用户 {openid} 更新成功。")
            return user
        logger.warning(f"尝试更新用户 {openid} 失败：用户不存在。")
        return None
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"更新用户 {openid} 失败: {e}", exc_info=True)
        return None

def get_user_by_openid(openid):
    """
    根据 openid 获取单个用户。
    :param openid: 用户的唯一标识符。
    :return: User 对象如果找到，否则返回 None。
    """
    try:
        user = User.query.filter_by(openid=openid).first() # 使用 first() 获取第一个匹配的结果
        if user:
            logger.info(f"成功获取用户 {openid}。")
            return user
        logger.info(f"用户 {openid} 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {openid} 失败: {e}", exc_info=True)
        return None

def get_all_users():
    """
    获取所有用户。
    :return: User 对象列表。
    """
    try:
        users = User.query.all() # 获取所有用户
        logger.info(f"成功获取所有用户列表，共 {len(users)} 条。")
        return users
    except SQLAlchemyError as e:
        logger.error(f"获取所有用户失败: {e}", exc_info=True)
        return []

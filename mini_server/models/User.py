from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from base import Base


class User(Base):
    __tablename__ = 'users' # 定义数据库表名，通常使用小写复数形式
    __table_args__ = {'extend_existing': True}

    # 定义表的列
    id = Column(Integer, primary_key=True) # 主键，自动递增
    nickname = Column(String(80), default='New User') # 昵称，默认值
    openid = Column(String(120), unique=True, nullable=False) # 用户的唯一标识符，唯一且非空
    height = Column(Float) # 身高
    weight = Column(Float) # 体重
    age = Column(Integer)  # 年龄
    gender = Column(String(10)) # 性别
    preferences = Column(String(500)) # 饮食偏好等
    allergies = Column(String(500)) # 过敏史
    diseases = Column(String(500)) # 疾病史
    activity_level = Column(String(50), default='lightly_active') # 活动水平，默认轻度活跃
    last_login_at = Column(DateTime, default=datetime.utcnow) # 最后登录时间，默认为当前 UTC 时间
    daily_energy_kcal = Column(Float, default=0.00) # 每日推荐能量摄入
    daily_carbohydrates_g = Column(Float, default=0.00) # 每日推荐碳水摄入
    daily_fat_g = Column(Float, default=0.00) # 每日推荐脂肪摄入
    daily_protein_g = Column(Float, default=0.00) # 每日推荐蛋白质摄入

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

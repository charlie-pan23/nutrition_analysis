from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Numeric, Time, Date, Text
from sqlalchemy.orm import relationship, backref
from base import Base

class MealRecord(Base):
    __tablename__ = 'meal_records'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_openid = Column(String(100), ForeignKey('users.openid', ondelete='CASCADE'), nullable=False, comment='用户openid')
    food_id = Column(Integer, ForeignKey('foods.id', ondelete='CASCADE'), nullable=False, comment='食物ID')
    meal_type_id = Column(Integer, ForeignKey('meal_types.id'), nullable=False, comment='餐食类型ID')
    amount = Column(Numeric(8, 2), default=100.00, nullable=False, comment='食用量(g)')
    unit = Column(String(20), default='g', comment='单位')
    calories = Column(Numeric(8, 2), default=0.00, comment='实际摄入热量(kcal)')
    carbs = Column(Numeric(8, 2), default=0.00, comment='实际摄入碳水化合物(g)')
    fat = Column(Numeric(8, 2), default=0.00, comment='实际摄入脂肪(g)')
    protein = Column(Numeric(8, 2), default=0.00, comment='实际摄入蛋白质(g)')
    fiber = Column(Numeric(8, 2), default=0.00, comment='实际摄入膳食纤维(g)')
    meal_date = Column(Date, nullable=False, comment='用餐日期')
    meal_time = Column(Time, comment='用餐时间')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 定义关系
    user = relationship('User', backref=backref('meal_records', lazy=True))
    food = relationship('Food', backref=backref('meal_records', lazy=True))
    meal_type = relationship('MealType', backref=backref('meal_records', lazy=True))

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

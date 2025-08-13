from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import declarative_base
from mini_server.base import Base


class MealType(Base):
    __tablename__ = 'meal_types'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, comment='餐食类型ID')
    name = Column(String(50), nullable=False, comment='餐食类型名称')
    start_time = Column(Time, comment='开始时间')
    end_time = Column(Time, comment='结束时间')

    def __repr__(self):
        return f'<MealType {self.id}: {self.name}>'

    def to_dict(self):
        """将餐食类型转换为字典（支持API响应）"""
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M:%S') if self.end_time else None
        }

    def is_current_meal(self, target_time=None):
        """判断给定时间是否在该餐食类型的时间范围内"""
        from datetime import datetime, time
        if target_time is None:
            target_time = datetime.now().time()

        # 处理夜宵的特殊跨天情况
        if self.id == 4:  # 夜宵
            # 夜宵时间范围：22:00:01 - 次日05:00:00
            return (target_time >= self.start_time) or (target_time <= self.end_time)

        # 处理其他正常时段
        if self.start_time and self.end_time:
            return self.start_time <= target_time <= self.end_time

        return False  # 加餐类型没有时间限制
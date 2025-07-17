from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from base import Base




# --- 1. 定义数据模型 (Food Model) ---
class Food(Base):
    __tablename__ = 'foods'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    calories = Column(Float, default=0.0) # 热量 (大卡，假设为每100g)
    protein = Column(Float, default=0.0) # 蛋白质 (克，假设为每100g)
    fat = Column(Float, default=0.0)     # 脂肪 (克，假设为每100g)
    carbs = Column(Float, default=0.0) # 碳水化合物 (克，假设为每100g)
    fiber = Column(Float, default=0.0)   # 新增：膳食纤维 (克，假设为每100g)
    comment = Column(String(500))

    def __repr__(self):
        return f'<Food {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbs': self.carbs,
            'fiber': self.fiber, # 新增
            'comment': self.comment
        }

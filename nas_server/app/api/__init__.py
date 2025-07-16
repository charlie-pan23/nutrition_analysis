# api/__init__.py
from flask import Blueprint

# 创建一个父级蓝图，用于封装所有的 API 路由
# 通常将其命名为 api_bp 或者 modules_bp 等
api_bp = Blueprint('api', __name__, url_prefix='/') # 或者您可以不设置url_prefix，让子蓝图各自处理

# 导入并注册所有子蓝图
# 注意：这里我们使用相对导入来确保正确的模块引用
from .user_routes import user_bp
from .food_routes import food_bp
from .meal_type_routes import meal_type_bp
from .meal_record_routes import meal_record_bp

# 将各个子蓝图注册到父级蓝图上
# 每个子蓝图的 url_prefix 将在其自身蓝图定义中处理
api_bp.register_blueprint(user_bp)
api_bp.register_blueprint(food_bp)
api_bp.register_blueprint(meal_type_bp)
api_bp.register_blueprint(meal_record_bp)

# 现在，当 app.py 导入 api_bp 时，所有这些子蓝图都将被包含在内。

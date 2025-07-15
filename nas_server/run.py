from dotenv import load_dotenv
from app import create_app
from app.extensions import socketio, db
from app.models.user import User
from app.models.meal_log import MealLog
from app.models.meal_item import MealItem
from app.models.food_nutrition import FoodNutrition

# 加载环境变量
load_dotenv()

# 创建应用实例
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Shell上下文处理器"""
    return {
        'db': db,
        'User': User,
        'MealLog': MealLog,
        'MealItem': MealItem,
        'FoodNutrition': FoodNutrition
    }


@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print("数据库初始化完成")


@app.cli.command()
def create_admin():
    """创建管理员用户"""
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("管理员用户创建完成")


if __name__ == '__main__':
    # 获取配置
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)

    print(f"🚀 启动服务器: http://{host}:{port}")
    print(f"🐛 调试模式: {'开启' if debug else '关闭'}")
    print(f"📊 数据库: {app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')}")

    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("✅ 数据库表创建完成")

    # 启动应用
    socketio.run(app, host=host, port=port, debug=debug)

# database.py
from flask_sqlalchemy import SQLAlchemy

# 创建 SQLAlchemy 实例
# 注意：这里不传入 Flask 应用实例，因为它将在 app.py 中通过 db.init_app(app) 绑定
db = SQLAlchemy()


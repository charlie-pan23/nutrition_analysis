# import os
#
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
#
# # 从环境变量获取数据库连接URI，提高安全性与可配置性
# # 格式：mysql+pymysql://用户名:密码@主机名:端口/数据库名
# # ⚠️ 注意：生产环境中，请务必使用环境变量来管理敏感信息！
# # 例如： export DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/nas"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
#     'DATABASE_URL',
#     'mysql+pymysql://root:123456@localhost:3306/nas' # 默认值，仅供开发测试，请勿用于生产！
# )
# # 关闭SQLAlchemy事件系统，减少不必要的内存开销和信号发送
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# # 初始化SQLAlchemy实例，与Flask应用关联
# db = SQLAlchemy(app)
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from app.extensions import db, login_manager, migrate
from app.config import Config
from app.utils.logger_utils import setup_logging
import logging


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 配置CORS
    CORS(app, origins="*")

    # 配置日志
    setup_logging(app)

    # 注册蓝图
    register_blueprints(app)

    # 创建SocketIO实例
    socketio = SocketIO(app, cors_allowed_origins="*")

    # 注册SocketIO事件
    register_socketio_events(socketio)

    return app, socketio


def register_blueprints(app):
    """注册蓝图"""
    from app.controllers.auth_controller import auth_bp
    from app.controllers.api_controller import api_bp
    from app.controllers.detection_controller import detection_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(detection_bp, url_prefix='/detection')


def register_socketio_events(socketio):
    """注册SocketIO事件"""
    from app.socketio_events.detection_events import register_detection_events
    register_detection_events(socketio)

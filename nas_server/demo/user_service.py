import os
from datetime import datetime

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError # 引入SQLAlchemy的异常类
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. Flask 应用初始化与数据库配置 ---
app = Flask(__name__)

# 从环境变量获取数据库连接URI，提高安全性与可配置性
# 格式：mysql+pymysql://用户名:密码@主机名:端口/数据库名
# ⚠️ 注意：生产环境中，请务必使用环境变量来管理敏感信息！
# 例如： export DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/nas"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:123456@localhost:3306/nas' # 默认值，仅供开发测试，请勿用于生产！
)
# 关闭SQLAlchemy事件系统，减少不必要的内存开销和信号发送
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化SQLAlchemy实例，与Flask应用关联
db = SQLAlchemy(app)

# --- 2. 定义数据模型 (User Model) ---
# 这就是ORM的魅力所在！我们用Python类来表示数据库中的表。
class User(db.Model):
    # 定义表名，如果类名和表名不一致，需要明确指定
    __tablename__ = 'users'

    # 定义列 (Column)
    id = db.Column(db.Integer, primary_key=True) # 主键，自动递增
    nickname = db.Column(db.String(80), default='New User') # 用户昵称，可为空，有默认值
    openid = db.Column(db.String(120), unique=True, nullable=False) # 用户唯一标识，唯一且不可为空
    height = db.Column(db.Float) # 身高
    weight = db.Column(db.Float) # 体重
    age = db.Column(db.Integer) # 年龄
    gender = db.Column(db.String(10)) # 性别
    preferences = db.Column(db.String(500)) # 偏好，增大长度以适应更多文本
    allergies = db.Column(db.String(500)) # 过敏信息，增大长度
    diseases = db.Column(db.String(500)) # 疾病信息，增大长度
    activity_level = db.Column(db.String(50), default='lightly_active') # 活动水平，有默认值，增大长度
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow) # 最后登录时间，默认UTC当前时间
    daily_energy_kcal = db.Column(db.Float, default=0.00) # 每日能量需求
    daily_carbohydrates_g = db.Column(db.Float, default=0.00) # 每日碳水化合物需求
    daily_fat_g = db.Column(db.Float, default=0.00) # 每日脂肪需求
    daily_protein_g = db.Column(db.Float, default=0.00) # 每日蛋白质需求

    # 定义一个__repr__方法，用于在打印对象时显示有意义的信息，便于调试
    def __repr__(self):
        return f'<User {self.openid}>'

    # 将User对象转换为字典，方便JSON序列化返回给前端
    def to_dict(self):
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
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'daily_energy_kcal': self.daily_energy_kcal,
            'daily_carbohydrates_g': self.daily_carbohydrates_g,
            'daily_fat_g': self.daily_fat_g,
            'daily_protein_g': self.daily_protein_g
        }

# --- 3. 数据库操作函数 (CRUD Operations) ---

# 添加用户
def add_user(**kwargs):
    try:
        # 创建User模型实例，传入所有参数
        new_user = User(**kwargs)
        # 将新用户对象添加到会话中
        db.session.add(new_user)
        # 提交会话，将数据写入数据库
        db.session.commit()
        logger.info(f"用户 {new_user.openid} 添加成功。")
        return new_user # 返回添加成功的用户对象
    except SQLAlchemyError as e:
        # 如果发生任何数据库错误，回滚事务
        db.session.rollback()
        logger.error(f"添加用户失败: {e}", exc_info=True)
        return None # 返回None表示失败

# 删除用户
def delete_user(openid):
    try:
        # 使用query查询方法，通过openid查找用户
        user = User.query.filter_by(openid=openid).first()
        if user:
            # 删除找到的用户对象
            db.session.delete(user)
            # 提交会话
            db.session.commit()
            logger.info(f"用户 {openid} 删除成功。")
            return True # 返回True表示删除成功
        logger.warning(f"尝试删除用户 {openid} 失败：用户不存在。")
        return False # 用户不存在
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"删除用户 {openid} 失败: {e}", exc_info=True)
        return False

# 更新用户信息
def update_user(openid, **kwargs):
    try:
        user = User.query.filter_by(openid=openid).first()
        if user:
            # 遍历kwargs字典，动态更新用户对象的属性
            for key, value in kwargs.items():
                if hasattr(user, key): # 检查属性是否存在，避免更新不存在的字段
                    setattr(user, key, value)
            # 提交会话，保存更改
            db.session.commit()
            logger.info(f"用户 {openid} 更新成功。")
            return user # 返回更新后的用户对象
        logger.warning(f"尝试更新用户 {openid} 失败：用户不存在。")
        return None # 用户不存在
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"更新用户 {openid} 失败: {e}", exc_info=True)
        return None

# 根据openid获取用户
def get_user_by_openid(openid):
    try:
        # 通过openid精确查找单个用户
        user = User.query.filter_by(openid=openid).first()
        if user:
            logger.info(f"成功获取用户 {openid}。")
            return user # 返回User对象
        logger.info(f"用户 {openid} 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {openid} 失败: {e}", exc_info=True)
        return None

# 获取所有用户
def get_all_users():
    try:
        # 查询User表中的所有记录
        users = User.query.all()
        logger.info(f"成功获取所有用户列表，共 {len(users)} 条。")
        return users # 返回User对象列表
    except SQLAlchemyError as e:
        logger.error(f"获取所有用户失败: {e}", exc_info=True)
        return []

# --- 4. Flask 路由示例 (将CRUD操作封装为API) ---
@app.route('/users', methods=['POST'])
def api_add_user():
    data = request.json
    if not data or 'openid' not in data:
        return jsonify({"error": "缺少openid或请求体为空"}), 400

    # 尝试获取已存在的用户，避免重复添加
    existing_user = get_user_by_openid(data['openid'])
    if existing_user:
        return jsonify({"message": f"用户 {data['openid']} 已存在。", "user": existing_user.to_dict()}), 200

    new_user = add_user(**data)
    if new_user:
        return jsonify({"message": "用户添加成功", "user": new_user.to_dict()}), 201
    return jsonify({"error": "用户添加失败"}), 500

@app.route('/users/<string:openid>', methods=['GET'])
def api_get_user(openid):
    user = get_user_by_openid(openid)
    if user:
        return jsonify({"message": "用户获取成功", "user": user.to_dict()}), 200
    return jsonify({"error": "用户未找到"}), 404

@app.route('/users/<string:openid>', methods=['PUT'])
def api_update_user(openid):
    data = request.json
    if not data:
        return jsonify({"error": "请求体为空"}), 400

    updated_user = update_user(openid, **data)
    if updated_user:
        return jsonify({"message": "用户更新成功", "user": updated_user.to_dict()}), 200
    return jsonify({"error": "用户更新失败或用户不存在"}), 404

@app.route('/users/<string:openid>', methods=['DELETE'])
def api_delete_user(openid):
    if delete_user(openid):
        return jsonify({"message": f"用户 {openid} 删除成功"}), 200
    return jsonify({"error": "用户删除失败或用户不存在"}), 404

@app.route('/users', methods=['GET'])
def api_get_all_users():
    users = get_all_users()
    logger.info(users[0].to_dict())
    logger.info('------------')
    # 将用户对象列表转换为字典列表，再转换为JSON
    return jsonify({"message": "所有用户获取成功", "users": [user.to_dict() for user in users]}), 200



@app.route('/wx_login/<code>', methods=['GET'])
def wx_login(code):
    appid = 'wxf07a5d5ce93485ad'
    secret = '0dba341f543a35cd764eddcd120d864e'
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    response = requests.get(url)
    logger.info("微信登录接口启动成功")
    logger.info(f"微信登录接口返回结果：{response.json()}")
    # 第一步：根据openid判断用户是否存在
    # 第二步：如果用户不存在，返回用户列表，让小程序端选中，去绑定用户
    # 第三步：如果用户存在，直接登录
    u = get_user_by_openid(response.json()['openid'])
    return u.to_dict()

# --- 5. 应用运行入口 ---
if __name__ == '__main__':
    logger.info("Flask 应用启动中...")
    app.run(host='0.0.0.0', port=6200, debug=True, threaded=True)

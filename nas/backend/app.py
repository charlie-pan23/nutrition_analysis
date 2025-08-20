import datetime
import sys
import os
import json
import time
from datetime import datetime
import atexit
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, Response, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from services.user_service import UserService
from services.camera_service import CameraService
from services.scale_test import ScaleService
from services.audio_service import AudioService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)  # 允许跨域访问
socketio = SocketIO(app, cors_allowed_origins="*")

user_service = UserService()
scale_service = ScaleService()
audio_service = AudioService()
camera_service = CameraService(server_ip='172.20.10.3')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("启动CameraService...")
camera_service.start()

# --------users--------
USER_DB_FILE = "Data/users.json"
current_user = None


@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(user_service.get_all_users())


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(user)


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get("name")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "用户名不能为空"}), 400

    try:
        new_user = user_service.create_user(name=name, role=role)

        # +++ 创建用户数据文件 +++
        user_data_file = os.path.join("Data", "users", f"{name}.json")
        if not os.path.exists(user_data_file):
            with open(user_data_file, 'w', encoding='utf-8') as f:
                json.dump({"meals": {}}, f, indent=2, ensure_ascii=False)
        # +++ 创建完成 +++

        return jsonify(new_user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        deleted_user = user_service.delete_user(user_id)
        return jsonify({"status": "success", "deleted_user": deleted_user["name"]})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    global current_user
    username = request.json.get('username')

    user = user_service.get_user_by_name(username)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    current_user = user

    # 启动硬件服务
    camera_service.start()
    scale_service.start()

    return jsonify({
        "message": f"{username} 欢迎登录",
        "user": {"id": user["id"], "name": user["name"]}
    })


@app.route('/api/logout')
def logout():
    """用户登出"""
    global current_user
    if current_user:
        print(f"用户 {current_user['name']} 登出")
    current_user = None

    # 关闭硬件服务
    camera_service.stop()
    scale_service.stop()
    return jsonify({"status": "success"})

@app.route('/api/current-user')
def get_current_user():
    """获取当前登录用户"""
    if not current_user:
        return jsonify({"error": "未登录"}), 401
    return jsonify({"id": current_user["id"], "name": current_user["name"]})


# --------users--------

# --------meals--------
@app.route('/api/user-meals', methods=['GET'])
def get_user_meals():
    """获取当前用户的所有餐食记录"""
    if not current_user:
        return jsonify({"error": "未登录"}), 401

    # 构建用户数据文件路径
    filename = os.path.join("Data", "users", f"{current_user['name']}.json")

    # +++ 检查并创建文件 +++
    if not os.path.exists(filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"meals": {}}, f, indent=2, ensure_ascii=False)
            return jsonify({"meals": []})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # +++ 检查完成 +++

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取所有餐食名称并排序（按时间倒序）
        meal_names = sorted(data.get("meals", {}).keys(), reverse=True)
        return jsonify({"meals": meal_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/meal-detail/<meal_name>', methods=['GET'])
def get_meal_detail(meal_name):
    """获取指定餐食的详细信息"""
    if not current_user:
        return jsonify({"error": "未登录"}), 401

    filename = os.path.join("Data", "users", f"{current_user['name']}.json")

    # +++ 检查并创建文件 +++
    if not os.path.exists(filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"meals": {}}, f, indent=2, ensure_ascii=False)
            return jsonify({"error": "用户数据不存在"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # +++ 检查完成 +++

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        meal_data = data.get("meals", {}).get(meal_name)

        if not meal_data:
            return jsonify({"error": "餐食记录不存在"}), 404

        return jsonify({
            "meal_name": meal_name,
            "meal_type": meal_data.get("meal_type", "未知餐食"),
            "foods": meal_data["foods"],
            "weight": meal_data.get("weight", 0),
            "timestamp": meal_data["formatted_time"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/record-meal', methods=['POST'])
def record_current_meal():
    """记录当前餐食"""
    if not current_user:
        return jsonify({"error": "未登录"}), 401

    # 构建用户数据文件路径
    filename = os.path.join("Data", "users", f"{current_user['name']}.json")

    # 检查并创建文件
    if not os.path.exists(filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"meals": {}}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    try:
        data = request.json
        meal_type = data.get("mealType", "未知餐食")
        current_weight = data.get("weight", 0)
        detected_foods = data.get("foods", [])  # 实际应用中从检测结果获取

        # 创建带餐食类型的键名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        meal_name = f"{meal_type}_{timestamp}"

        # 读取用户数据
        with open(filename, 'r', encoding='utf-8') as f:
            user_data = json.load(f)

        # 添加新餐食记录
        user_data["meals"][meal_name] = {
            "foods": detected_foods,
            "weight": current_weight,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "meal_type": meal_type  # 保存餐食类型
        }

        # 保存数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success", "meal_name": meal_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------meals--------


# --------scale--------
@app.route('/api/weight')
def get_weight():
    return jsonify({"weight": scale_service.get_weight()})
    # return jsonify({"weight": 198})

# --------scale--------


# --------camera--------
def gen_frames():
    """
    生成器函数：持续从CameraService获取最新的处理后视频帧，
    并将其以multipart/x-mixed-replace格式返回，用于浏览器实时显示。
    """
    logging.info("视频流生成器启动。")
    while True:
        # 从CameraService获取最新的处理后的帧
        frame = CameraService.get_processed_frame()
        if frame is not None:
            # 构建multipart响应的每一部分
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # 如果暂时没有帧可用，等待一小段时间，避免CPU空转
            time.sleep(0.05)


@app.route('/video_feed')
def video_feed():
    """
    视频流路由：返回一个实时的M-JPEG流，浏览器可以直接显示。
    """
    logging.info("客户端连接到 '/video_feed'。")
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# --------camera--------


# --------shutdown --------
def shutdown_services():
    print("应用关闭，释放资源...")
    camera_service.stop()
    scale_service.stop()
    # audio_service.stop_recording()


atexit.register(shutdown_services)
# --------shutdown --------

if __name__ == '__main__':
    os.makedirs("recordings", exist_ok=True)
    os.makedirs("Data/users", exist_ok=True)
    scale_service.start()
    logging.info("启动树莓派上的Flask应用...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logging.critical(f"Flask 应用启动失败: {e}")
    finally:
        logging.info("Flask 应用关闭，正在停止所有service...")
        shutdown_services()

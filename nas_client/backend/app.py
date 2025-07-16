from datetime import datetime
import sys
import os
import json
import time
import atexit
import logging
import threading

import requests

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

SERVER_IP = "172.20.10.3"
SERVER_PORT = 5000

user_service = UserService()
scale_service = ScaleService()
audio_service = AudioService()
camera_service = CameraService(server_ip=SERVER_IP)

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


@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get("name")
    role = data.get("role")

    try:
        updated_user = user_service.update_user(user_id=user_id, name=name, role=role)
        return jsonify(updated_user)
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


# @app.route('/api/logout')
# def logout():
#     global current_user
#     if current_user:
#         print(f"用户 {current_user['name']} 登出")
#     current_user = None
#
#     # 关闭硬件服务
#     camera_service.stop()
#     scale_service.stop()
#
#     # 确保服务完全停止
#     time.sleep(0.2)
#
#     return jsonify({"status": "success"})

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

# --------data--------
SERVER_BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/data"


def send_data_to_server(stage_name: str, payload: dict) -> dict:
    """
    通用函数，用于向服务器发送指定阶段的JSON数据。
    """
    data_to_send = {"stageName": stage_name}  # Key updated to English
    data_to_send.update(payload)

    try:
        print(f"\nSending stage '{stage_name}' data to server...")
        print(f"Data to send: {json.dumps(data_to_send, indent=4, ensure_ascii=False)}")

        response = requests.post(SERVER_BASE_URL, json=data_to_send, timeout=10)
        response.raise_for_status()

        server_response = response.json()
        print(f"Server response ({response.status_code}):")
        print(json.dumps(server_response, indent=4, ensure_ascii=False))
        return server_response
    except requests.exceptions.Timeout:
        print(f"Error: Server connection timed out. Check network or server status.")
        return {}
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server '{SERVER_BASE_URL}'. Check IP, port, or network.")
        return {}
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP request failed with status code {e.response.status_code}. Response: {e.response.text}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Server response is not valid JSON.")
        return {}
    except Exception as e:
        print(f"An unknown error occurred: {e}")
        return {}


def send_initialization_status(
        scale_service_started: bool,
        camera_service_started: bool,
        audio_service_started: bool,
        backend_started: bool,
        frontend_started: bool
) -> dict:
    """
    Sends Raspberry Pi client service initialization status to the server.
    """
    ready = (scale_service_started and camera_service_started and
             audio_service_started and backend_started and frontend_started)

    payload = {
        "scaleServiceStarted": scale_service_started,
        "cameraServiceStarted": camera_service_started,
        "audioServiceStarted": audio_service_started,
        "backendStarted": backend_started,
        "frontendStarted": frontend_started,
        "ready": ready
    }
    return send_data_to_server("0", payload)


def send_user_info_selection(selected_user_info: str = "") -> dict:
    """
    Sends user selection information to the server.
    """
    payload = {
        "selectedUserInfo": selected_user_info
    }
    return send_data_to_server("1", payload)


def send_normal_operation_data(
        exit_requested: bool,
        weight: float,
        voice_workflow_request: str,
        text_workflow_request: str,
        meal_record_changed: bool,
        change_content: dict = None
) -> dict:
    """
    Sends normal operation stage data from Raspberry Pi to the server.
    """
    payload = {
        "exitRequested": exit_requested,
        "weight": weight,
        "voiceWorkflowRequest": voice_workflow_request,
        "textWorkflowRequest": text_workflow_request,
        "mealRecordChanged": meal_record_changed
    }

    if meal_record_changed:
        if change_content is None:
            print("⚠️ Warning: Meal record changed but 'changeContent' is empty. Please provide content.")
        payload["changeContent"] = change_content
    else:
        payload["changeContent"] = None

    return send_data_to_server("2", payload)


def client_communication_thread():
    logging.info("--- Raspberry Pi Client Communication Thread Starting ---")

    # 1. 初始化阶段
    logging.info("\n--- Entering Initialization Stage ---")
    init_success = False
    max_retries = 5
    for attempt in range(max_retries):
        logging.info(f"Attempting to connect to server (Attempt {attempt + 1}/{max_retries})...")
        server_init_response = send_initialization_status(
            scale_service_started=True,
            camera_service_started=True,
            audio_service_started=True,
            backend_started=True,
            frontend_started=True
        )
        if server_init_response and server_init_response.get("ready"):
            logging.info("Server initialization confirmed!")
            init_success = True
            break
        else:
            logging.info("Server not ready yet, waiting...")
            time.sleep(2)

    if not init_success:
        logging.error("Failed to complete initialization. Please check server status. Communication thread exiting.")
        return

    # 2. 初始化用户信息阶段
    logging.info("\n--- Entering User Info Initialization Stage ---")
    # 模拟选择用户 "user_xyz"
    user_info_response = send_user_info_selection("user_xyz")
    if user_info_response:
        # 访问服务器的英文响应键
        logging.info(f"Current user list: {user_info_response.get('userList')}")
        # 这里你可以根据服务器返回的用户列表更新本地显示

    # 3. 正常运行阶段
    logging.info("\n--- Entering Normal Operation Stage ---")
    running = True
    while running:
        # 模拟获取传感器数据、用户输入等
        current_weight = 100.0 + (time.time() % 10)  # 模拟重量变化
        voice_req = ""
        text_req = ""
        meal_changed = False
        meal_content = None

        # 模拟每隔一段时间发送一次数据，或者根据事件触发
        if int(time.time()) % 15 == 0:  # 模拟每15秒用户请求语音识别
            voice_req = "identify current item"
            logging.info("\nSimulating user voice request: 'identify current item'")

        if int(time.time()) % 20 == 0:  # 模拟每20秒餐食记录变化
            meal_changed = True
            meal_content = {
                "action": "add",
                "item": "simulated_food_" + str(int(time.time()) % 100),
                "quantity": 1,
                "calories": 50,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            logging.info(f"\nSimulating meal record change: {meal_content}")

        # 发送正常运行数据
        normal_op_response = send_normal_operation_data(
            exit_requested=False,
            weight=current_weight,
            voice_workflow_request=voice_req,
            text_workflow_request=text_req,
            meal_record_changed=meal_changed,
            change_content=meal_content
        )

        # 处理服务器响应 (使用英文键名)
        if normal_op_response:
            if normal_op_response.get("recognitionResult"):
                logging.info(f"Server recognized: {normal_op_response['recognitionResult']}")
            if normal_op_response.get("voiceWorkflowStatus"):
                logging.info(f"Voice status: {normal_op_response['voiceWorkflowStatus']}")
            if normal_op_response.get("textWorkflowResponse"):
                logging.info(f"Text response: {normal_op_response['textWorkflowResponse']}")
            if normal_op_response.get("mealRecordChanged"):
                logging.info(f"Meal record change confirmed: {normal_op_response.get('changeContent')}")

        # 检查是否应该退出 (例如，从用户输入或服务器响应中获取退出信号)
        # 这里仅作示例，实际退出逻辑会更复杂
        if normal_op_response.get("exitRequested_serverConfirmation"):  # 假设服务器会返回一个确认退出的字段
            running = False
            logging.info("Received server's exit confirmation, communication thread is shutting down.")

        time.sleep(0.5)  # 每2秒发送一次心跳或数据更新

    logging.info("--- Client Communication Thread Shut Down ---")


# --------data--------


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

    # 启动 scale_service (保持不变)
    scale_service.start()
    logging.info("Scale service started successfully.")

    # 创建并启动客户端通信线程
    client_thread = threading.Thread(target=client_communication_thread, daemon=True)  # daemon=True 确保主程序退出时线程也退出
    client_thread.start()
    logging.info("Raspberry Pi client communication thread started in background.")

    # 启动 Flask 应用 (保持不变，它会在主线程中运行并阻塞)
    logging.info("Starting Flask application on Raspberry Pi...")
    try:
        # app.run() 应该在你 app.py 文件中 Flask 实例定义之后
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)  # threaded=True 允许 Flask 内部处理多个请求
    except Exception as e:
        logging.critical(f"Flask application failed to start: {e}")
    finally:
        logging.info("Flask application closing, shutting down all services...")
        shutdown_services()

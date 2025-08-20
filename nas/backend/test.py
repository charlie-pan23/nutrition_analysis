import sys
import os
import json
import time
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, Response
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
camera_service = CameraService()
scale_service = ScaleService()
audio_service = AudioService()



#--------users--------
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


@app.route('/api/current-user')
def get_current_user():
    """获取当前登录用户"""
    if not current_user:
        return jsonify({"error": "未登录"}), 401
    return jsonify({"id": current_user["id"], "name": current_user["name"]})

#--------users--------



#--------init --------
@app.route('/services/init')
def init_app():
    camera_service.start()
    scale_service.start()

#--------init --------


#--------scale--------
@app.route('/api/weight')
def get_weight():
    return jsonify({"weight": scale_service.get_weight()})

@app.route('/video_feed')
def video_feed():
    def generate():
        while camera_service.active:
            frame = camera_service.get_jpeg_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' +
                       frame + b'\r\n')
            time.sleep(0.1)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
#--------scale--------



#--------camera--------



#--------camera--------



#--------audio--------
@app.route('/api/start-recording')
def start_recording():
    if audio_service.start_recording():
        return jsonify({"status": "started"})
    return jsonify({"error": "录音已在进行中"}), 400

@app.route('/api/stop-recording')
def stop_recording():
    if not audio_service.recording:
        return jsonify({"error": "没有正在进行的录音"}), 400

    filename = f"recordings/recording_{int(time.time())}.wav"
    audio_service.stop_recording_and_save(filename)
    duration = audio_service.get_recording_duration()
    return jsonify({
        "status": "success",
        "file": filename,
        "duration": duration
    })

def run_server():
    os.makedirs("recordings", exist_ok=True)
    app.run(host='0.0.0.0', port=5000, threaded=True)

#--------audio--------


#--------advice --------
@app.route('/api/run-workflow', methods=['POST'])
def run_workflow(name):
    sound_path = request.json.get('sound_path', name)
    weight_path = request.json.get('weight_path', 'weight.txt')

    sound_id = audio_service.upload_file(sound_path, "AUDIO", "audio/wav")
    weight_id = audio_service.upload_file(weight_path, "TXT", "text/plain")

    if sound_id and weight_id:
        result = audio_service.run_workflow(sound_id, weight_id)
        if result and "data" in result:
            outputs = result['data'].get('outputs', {})
            output_text = outputs.get("output") or outputs.get("voice_text") or outputs.get("text")
            if output_text:
                print("识别结果：", output_text)
                audio_service.speak(output_text)
                return jsonify({"result": output_text})
            else:
                return jsonify({"error": "未找到有效输出字段"}), 500
        else:
            return jsonify({"error": "Workflow 无有效输出"}), 500
    else:
        return jsonify({"error": "文件上传失败，无法运行 workflow"}), 500

#--------advice --------

if __name__ == '__main__':
    run_server()

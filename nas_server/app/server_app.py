from flask import Flask, request, Response, jsonify
import logging
import threading
import time
import requests
import json

# --- 导入数据管理、YOLO服务和 MySQL 服务类 ---
from services.data_manager import DataManager
from services.yolo_service import YOLOService
from services.mysql_service import MySQLService

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- YOLO 模型路径配置 ---
MODEL_PATH = 'yolo/yolov8n_weights/weights/best.pt' # 确保此路径正确

# --- MySQL 数据库配置 ---
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'nas'
}

stage = 0 # 阶段标记，用于标识当前服务的状态
SEND_INTERVAL = 0.5  # 每秒发送 2 次
SEND_URL = "http://172.20.10.11:5000"

# --- 实例化数据管理器、YOLO服务和 MySQL 服务 ---
data_manager = DataManager()
yolo_service = YOLOService(MODEL_PATH, data_manager) # 实例化 YOLOService
mysql_service = MySQLService(MYSQL_CONFIG, data_manager) # 实例化 MySQLService



#-----yolo------
@app.route('/process_frame', methods=['POST'])
def process_frame():
    """
    接收树莓派发送的图像帧，调用YOLO服务执行推理，并将处理后的图像（带检测框）返回。
    适用于视频流显示。
    """
    processed_image_bytes, error_msg = yolo_service.process_frame_for_display(request.data)
    if error_msg:
        status_code = 500 if "模型未加载" in error_msg or "服务器内部错误" in error_msg else 400
        return Response(error_msg, status=status_code)
    return Response(processed_image_bytes, mimetype='image/jpeg')

@app.route('/get_detections_json', methods=['POST'])
def get_detections_json():
    """
    接收图像帧，调用YOLO服务执行推理，并返回纯粹的检测结果JSON数据。
    适用于微信小程序等需要结构化数据的场景。
    """
    detections_dict, error_msg = yolo_service.get_detections_as_json(request.data)
    if error_msg:
        status_code = 500 if "模型未加载" in error_msg or "服务器内部错误" in error_msg else 400
        return jsonify({"error": error_msg}), status_code
    return jsonify(detections_dict)

#-----yolo------

def async_send_data_periodically(data_manager):
    def send_loop():
        while True:
            try:
                data = data_manager.get_data_to_send()  # 获取当前 data_to_send
                requests.post(SEND_URL, json=data, timeout=1)
                logging.info("已异步发送 data_to_send")
            except Exception as e:
                logging.error(f"发送 data_to_send 失败: {e}")
            time.sleep(SEND_INTERVAL)

    thread = threading.Thread(target=send_loop, daemon=True)
    thread.start()






# --- 主程序入口 ---
if __name__ == "__main__":
    logging.info("启动 Windows PC 上的统一服务器应用...")

    # 1. 在独立线程中启动 YOLO 模型加载（通过 YOLOService）
    yolo_service.start_model_loading_in_thread()

    # 2. 在独立线程中启动 MySQL 数据库连接（通过 MySQLService）
    mysql_service.start_connection_in_thread()

    # 3. 启动异步发送 data_to_send 的线程
    async_send_data_periodically(data_manager)

    # 4. 启动 Flask 应用
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


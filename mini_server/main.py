import asyncio
import threading

import requests
from flask import Flask, request, Response, jsonify
import cv2
import numpy as np
import torch
from io import BytesIO
from PIL import Image
import logging
import os

from flask_cors import CORS
from ultralytics import YOLO
from flask import Flask, jsonify
import time

from routes.analysis import analysis_bp
from routes.wx import wx_bp
from routes.meal_type import type_bp
from routes.meal_record import record_bp
from routes.user import user_bp
from routes.food import food_bp
from service.food_service import get_food_by_name
app = Flask(__name__)
app.register_blueprint(wx_bp)
app.register_blueprint(type_bp)
app.register_blueprint(record_bp)
app.register_blueprint(user_bp)
app.register_blueprint(food_bp)
app.register_blueprint(analysis_bp)

MODEL_PATH = 'yolo/yolov8n_weights/weights/best.pt'

model = None  # 初始化模型变量为 None
device = 'cpu'  # 默认设备为 CPU
CORS(app)
from mini_server.cache_manager import global_cache as cache  # ✅ 使用全局 cache

# 在应用程序启动时加载YOLO模型，确保只加载一次
if not os.path.exists(MODEL_PATH):
    logging.critical(f"YOLOv8模型文件未找到: {MODEL_PATH}。请检查路径或文件是否存在。")
else:
    try:
        logging.info(f"正在加载YOLOv8模型: {MODEL_PATH}...")

        if torch.cuda.is_available():
            device = 'cuda'  # 如果有CUDA，则使用GPU
            logging.info(f"检测到CUDA可用！YOLOv8模型将加载到 GPU ({torch.cuda.get_device_name(0)}) 上运行。")
            model = YOLO(MODEL_PATH, task='detect').to(device)  # 显式将模型移到GPU
        else:
            device = 'cpu'
            logging.warning("未检测到CUDA可用，或CUDA环境未正确配置。YOLOv8模型将回退到 CPU 上运行。")
            model = YOLO(MODEL_PATH, task='detect').to(device)  # 显式将模型移到CPU

        logging.info(f"YOLOv8模型加载成功并已部署到 {device}。")

    except Exception as e:
        logging.critical(f"无法加载YOLOv8模型: {e}")
        logging.critical("请检查您的PyTorch和ultralytics安装，以及best.pt文件是否损坏或与YOLOv8模型版本不兼容。")
        logging.critical("特别注意PyTorch的CUDA版本是否与您的显卡驱动兼容。")


# --- YOLO process ---

def process_image_for_yolo(image_data):
    """
    通用图像处理函数，将接收到的图像数据转换为YOLO模型可处理的格式。
    """
    if not image_data:
        logging.warning("收到空图像数据。")
        return None, "没有接收到图像数据。"

    try:
        image = Image.open(BytesIO(image_data))
        # YOLOv8的模型接受PIL Image或NumPy数组 (HWC, RGB)
        img_np_rgb = np.array(image)
        return img_np_rgb, None
    except Exception as e:
        logging.error(f"图像解码失败: {e}", exc_info=True)
        return None, "图像解码失败。"


def rate_limited(interval=3):
    """
    装饰器，限制函数执行频率，至少间隔 interval 秒才能再次执行
    """
    def decorator(func):
        last_called = [0.0]  # 使用列表以便在嵌套函数中修改

        def wrapper(*args, **kwargs):
            nonlocal last_called
            elapsed = time.time() - last_called[0]
            if elapsed < interval:
                print(f"调用被限制，需等待 {interval - elapsed:.2f} 秒")
                return None  # 或者 raise Exception("Too many requests")
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limited(interval=3)
def my_function(res):
    run_async_in_thread(my_async_func(res))

def run_async_in_thread(coro):
    def _run():
        asyncio.run(coro)
    thread = threading.Thread(target=_run)
    thread.start()

async def my_async_func(res):
    formatted_detections = []
    # YOLOv8的 Boxes 对象可以直接获取检测结果
    # res[0].boxes 是一个 Boxes 对象
    for box in res[0].boxes:
        # xyxy 是边界框的左上角和右下角坐标 [x1, y1, x2, y2]
        # conf 是置信度
        # cls 是类别ID
        x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
        confidence = float(box.conf[0].tolist())
        class_id = int(box.cls[0].tolist())

        # 可以在此处通过 model.names 字典获取类别名称
        class_name = model.names[class_id] if model.names else f"class_{class_id}"

        formatted_detections.append({
            "box": [x1, y1, x2, y2],
            "confidence": confidence,
            "class_id": class_id,
            "class_name": class_name
        })

    logging.info(f"处理并发送JSON检测结果。检测到 {len(formatted_detections)} 个目标。")
    cache.set('detections', formatted_detections)
    response = requests.get('http://172.20.10.11:5000/api/weight')
    response_data = response.json()
    cache.set('weight', response_data['weight'])


@app.route('/process_frame', methods=['POST'])
def process_frame():
    """
    接收树莓派发送的图像帧，执行YOLO推理，并将处理后的图像（带检测框）返回。
    适用于视频流显示。
    """
    if model is None:
        logging.error("YOLOv8模型未加载，无法处理帧。")
        return Response("YOLOv8模型未加载，服务器内部错误。", status=500)

    img_np_rgb, error_msg = process_image_for_yolo(request.data)
    if img_np_rgb is None:
        return Response(error_msg, status=400)

    try:
        # 执行YOLOv8推理
        # YOLOv8的 predict 方法可以直接接收PIL图像或NumPy数组 (HWC, RGB)
        # verbose=False 可以减少控制台输出的推理信息
        results = model.predict(img_np_rgb, verbose=False)

        ## 分析图片并获取检测结果，本地缓存
        my_function(results)

        # 获取带检测框的图像
        # results 是一个 Results 对象列表 (因为可以处理多张图片，这里只有一张)
        # results[0].plot() 会返回一个NumPy数组 (BGR格式)
        img_result_bgr = results[0].plot()
        img_result_rgb_for_frontend = cv2.cvtColor(img_result_bgr, cv2.COLOR_BGR2RGB)
        ret, img_encoded_bytes = cv2.imencode('.jpg', img_result_rgb_for_frontend, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        if not ret:
            logging.error("无法将处理后的帧编码为JPEG。")
            return Response("服务器处理图像时出错。", status=500)

        logging.info(f"处理并发送带框帧回树莓派。大小: {len(img_encoded_bytes.tobytes())} 字节。")

        return Response(img_encoded_bytes.tobytes(), mimetype='image/jpeg')

    except Exception as e:
        logging.error(f"处理图像并渲染时发生错误: {e}", exc_info=True)
        return Response(f"服务器内部错误: {e}", status=500)


@app.route('/get_detections_json', methods=['post'])
def get_detections_json():
    detections = cache.get('detections')
    weight = cache.get('weight')

    if not weight:
        return jsonify({"code": 400,"msg": "称重数据不存在"})

    print("==========================")
    print(detections)
    if not detections:
        return jsonify({"code": 400,"msg": "暂无数据"})

    class_name = detections[0]["class_name"]
    if not class_name:
        return jsonify({"code": 400, "msg": "识别出错"})



    food = get_food_by_name(class_name)

    if not food:
        return jsonify({"code": 400, "msg": "食物不存在"})

    return jsonify({"data": {
        "food_id":food.id,
        "name":food.name,
        "amount":weight,
        "calories":round(food.calories * weight/100,2),
        "protein":round(food.protein * weight/100,2),
        "fat":round(food.fat * weight/100,2),
        "carbs":round(food.carbs * weight/100,2),
        "fiber":round(food.fiber * weight/100,2)
    },"code": 200})


# 测试执行
if __name__ == "__main__":
    get_food_by_name("apple")
    logging.info("在Windows上启动Flask服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


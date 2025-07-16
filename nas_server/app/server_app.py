from flask import Flask, request, Response, jsonify
from flask_cors import CORS  # 导入 CORS 模块
import cv2
import numpy as np
import torch
from io import BytesIO
from PIL import Image
import logging
import os

from ultralytics import YOLO
from services.database import db
from api.user_routes import user_bp
from api.food_routes import food_bp
from api.meal_type_routes import meal_type_bp
from api.meal_record_routes import meal_record_bp

# from services.user_service import User
# from services.food_service import Food
# from services.meal_type_service import MealType
# from services.meal_record_service import MealRecord

from api import api_bp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 从环境变量获取数据库连接URI，提高安全性与可配置性
# 格式：mysql+pymysql://用户名:密码@主机名:端口/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:123456@localhost:3306/nas' # 默认值，仅供开发测试，请勿用于生产！
)

# 关闭SQLAlchemy事件系统，减少不必要的内存开销和信号发送
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 绑定 SQLAlchemy 实例到 Flask 应用
db.init_app(app)

# 注册蓝图
# 将各个蓝图注册到主应用中
app.register_blueprint(user_bp)
app.register_blueprint(food_bp)
app.register_blueprint(meal_type_bp)
app.register_blueprint(meal_record_bp)

# --- YOLO 模型加载配置 ---

MODEL_PATH = 'yolo/yolov8n_weights/weights/best.pt'

model = None  # 初始化模型变量为 None
device = 'cpu'  # 默认设备为 CPU

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


# --- YOLO 模型加载结束 ---

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

        # 获取带检测框的图像
        # results 是一个 Results 对象列表 (因为可以处理多张图片，这里只有一张)
        # results[0].plot() 会返回一个NumPy数组 (BGR格式)
        img_result_bgr = results[0].plot()

        ret, img_encoded_bytes = cv2.imencode('.jpg', img_result_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if not ret:
            logging.error("无法将处理后的帧编码为JPEG。")
            return Response("服务器处理图像时出错。", status=500)

        logging.info(f"处理并发送带框帧回树莓派。大小: {len(img_encoded_bytes.tobytes())} 字节。")

        return Response(img_encoded_bytes.tobytes(), mimetype='image/jpeg')

    except Exception as e:
        logging.error(f"处理图像并渲染时发生错误: {e}", exc_info=True)
        return Response(f"服务器内部错误: {e}", status=500)


@app.route('/get_detections_json', methods=['POST'])
def get_detections_json():
    # """
    # 接收图像帧，执行YOLOv8推理，并返回纯粹的检测结果JSON数据。
    # 适用于微信小程序等需要结构化数据的场景。
    # """
    # if model is None:
    #     logging.error("YOLOv8模型未加载，无法处理帧。")
    #     return jsonify({"error": "YOLOv8模型未加载，服务器内部错误。"}), 500
    #
    # img_np_rgb, error_msg = process_image_for_yolo(request.data)
    # if img_np_rgb is None:
    #     return jsonify({"error": error_msg}), 400
    #
    # try:
    #     # 执行YOLOv8推理
    #     results = model.predict(img_np_rgb, verbose=False)
    #
    #     formatted_detections = []
    #     # YOLOv8的 Boxes 对象可以直接获取检测结果
    #     # results[0].boxes 是一个 Boxes 对象
    #     for box in results[0].boxes:
    #         # xyxy 是边界框的左上角和右下角坐标 [x1, y1, x2, y2]
    #         # conf 是置信度
    #         # cls 是类别ID
    #         x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
    #         confidence = float(box.conf[0].tolist())
    #         class_id = int(box.cls[0].tolist())
    #
    #         # 可以在此处通过 model.names 字典获取类别名称
    #         class_name = model.names[class_id] if model.names else f"class_{class_id}"
    #
    #         formatted_detections.append({
    #             "box": [x1, y1, x2, y2],
    #             "confidence": confidence,
    #             "class_id": class_id,
    #             "class_name": class_name
    #         })
    #
    #     logging.info(f"处理并发送JSON检测结果。检测到 {len(formatted_detections)} 个目标。")
    #
    #     return jsonify({"detections": formatted_detections})
    #
    # except Exception as e:
    #     logging.error(f"处理图像并生成JSON时发生错误: {e}", exc_info=True)
    #     return jsonify({"error": f"服务器内部错误: {e}"}), 500
    #
    dict = [{
        "name": "牛奶",
        "weight": 100,
        "calories": 150,
        "protein": 8,
        "fat": 5,
        "carbohydrates": 12
    }, {
        "name": "黄瓜",
        "weight": 120,
        "calories": 20,
        "protein": 8,
        "fat": 15,
        "carbohydrates": 22
    }]
    return jsonify(dict), 200


@app.route('/hello')  # 默认只支持 GET
def hello():
    return "Hello"


if __name__ == '__main__':
    logging.info("启动Windows PC上的Flask服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

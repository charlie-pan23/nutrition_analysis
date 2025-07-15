import logging
import os
import torch
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import threading
import json
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YOLOService:
    def __init__(self, model_path: str, server_data_manager):

        self.model_path = model_path
        self.server_data_manager = server_data_manager # 接收数据管理器实例
        self.model = None
        self.device = 'cpu' # 默认设备
        self._model_loading_lock = threading.Lock() # 用于模型加载的锁，防止并发问题

    def _initialize_model(self):
        """
        私有方法：初始化 YOLOv8 模型。
        此方法在单独的线程中调用，以避免阻塞主线程。
        加载成功后会更新 server_data_manager 中的 YOLO 状态。
        此逻辑精准复刻了您提供的“测试成功”的YOLO模型加载部分。
        """
        with self._model_loading_lock:
            if self.model is not None:
                logging.info("YOLO模型已加载，无需重复加载。")
                self.server_data_manager.set_yolo_ready(True) # 确保状态正确
                return

            if not os.path.exists(self.model_path):
                logging.critical(f"YOLOv8模型文件未找到: {self.model_path}。请检查路径或文件是否存在。")
                self.server_data_manager.set_yolo_ready(False)
                return # 模型文件不存在，直接退出

            try:
                logging.info(f"正在加载YOLOv8模型: {self.model_path}...")

                if torch.cuda.is_available():
                    self.device = 'cuda'  # 如果有CUDA，则使用GPU
                    logging.info(f"检测到CUDA可用！YOLOv8模型将加载到 GPU ({torch.cuda.get_device_name(0)}) 上运行。")
                    self.model = YOLO(self.model_path, task='detect').to(self.device)  # 显式将模型移到GPU
                else:
                    self.device = 'cpu'
                    logging.warning("未检测到CUDA可用，或CUDA环境未正确配置。YOLOv8模型将回退到 CPU 上运行。")
                    self.model = YOLO(self.model_path, task='detect').to(self.device)  # 显式将模型移到CPU

                logging.info(f"YOLOv8模型加载成功并已部署到 {self.device}。")
                self.server_data_manager.set_yolo_ready(True) # 模型加载成功，更新状态

            except Exception as e:
                logging.critical(f"无法加载YOLOv8模型: {e}")
                logging.critical("请检查您的PyTorch和ultralytics安装，以及best.pt文件是否损坏或与YOLOv8模型版本不兼容。")
                logging.critical("特别注意PyTorch的CUDA版本是否与您的显卡驱动兼容。")
                self.server_data_manager.set_yolo_ready(False) # 模型加载失败，更新状态

    def start_model_loading_in_thread(self):
        """在独立线程中启动 YOLO 模型的异步加载。"""
        logging.info("启动YOLO模型异步加载线程。")
        yolo_thread = threading.Thread(target=self._initialize_model, daemon=True)
        yolo_thread.start()

    def _process_image_data_for_yolo(self, image_data: bytes):
        """
        私有方法：解码图像数据并准备用于 YOLO 推理。
        此逻辑精准复刻了您提供的“测试成功”的process_image_for_yolo函数。
        :param image_data: 图像的原始字节数据。
        :return: (numpy.ndarray, error_message) 如果成功返回 numpy 图像数组，否则返回 None 和错误信息。
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

    def process_frame_for_display(self, image_data: bytes) -> tuple[bytes | None, str | None]:
        """
        接收图像帧，执行YOLO推理，并将处理后的图像（带检测框）返回。
        适用于视频流显示。
        此逻辑精准复刻了您提供的“测试成功”的process_frame路由处理。
        :param image_data: 原始图像字节数据。
        :return: (processed_image_bytes, error_message) 如果成功返回处理后的图片字节，否则返回 None 和错误信息。
        """
        # 检查模型是否已加载且就绪
        if self.model is None or not self.server_data_manager.get_yolo_ready():
            logging.error("YOLOv8模型未加载或未准备就绪，无法处理帧。")
            return None, "YOLOv8模型未加载或未准备就绪。"

        img_np_rgb, error_msg = self._process_image_data_for_yolo(image_data)
        if img_np_rgb is None:
            return None, error_msg

        try:
            results = self.model.predict(img_np_rgb, verbose=False)
            img_result_bgr = results[0].plot()

            ret, img_encoded_bytes = cv2.imencode('.jpg', img_result_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            if not ret:
                logging.error("无法将处理后的帧编码为JPEG。")
                return None, "服务器处理图像时出错。"

            logging.info(f"处理并发送带框帧。大小: {len(img_encoded_bytes.tobytes())} 字节。")
            return img_encoded_bytes.tobytes(), None

        except Exception as e:
            logging.error(f"执行YOLO推理或渲染时发生错误: {e}", exc_info=True)
            return None, f"服务器内部错误: {e}"

    def get_detections_as_json(self, image_data: bytes) -> tuple[dict | None, str | None]:
        """
        接收图像帧，执行YOLOv8推理，并返回纯粹的检测结果JSON数据。
        适用于微信小程序等需要结构化数据的场景。
        此逻辑精准复刻了您提供的“测试成功”的get_detections_json路由处理。
        :param image_data: 原始图像字节数据。
        :return: (detections_dict, error_message) 如果成功返回检测结果字典，否则返回 None 和错误信息。
        """
        # 检查模型是否已加载且就绪
        if self.model is None or not self.server_data_manager.get_yolo_ready():
            logging.error("YOLOv8模型未加载或未准备就绪，无法处理帧。")
            return None, "YOLOv8模型未加载或未准备就绪。"

        img_np_rgb, error_msg = self._process_image_data_for_yolo(image_data)
        if img_np_rgb is None:
            return None, error_msg

        try:
            results = self.model.predict(img_np_rgb, verbose=False)
            formatted_detections = []
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                confidence = float(box.conf[0].tolist())
                class_id = int(box.cls[0].tolist())
                class_name = self.model.names[class_id] if self.model.names else f"class_{class_id}"
                formatted_detections.append({
                    "box": [x1, y1, x2, y2],
                    "confidence": confidence,
                    "class_id": class_id,
                    "class_name": class_name
                })

            logging.info(f"生成JSON检测结果。检测到 {len(formatted_detections)} 个目标。")
            return {"detections": formatted_detections}, None

        except Exception as e:
            logging.error(f"执行YOLO推理或生成JSON时发生错误: {e}", exc_info=True)
            return None, f"服务器内部错误: {e}"


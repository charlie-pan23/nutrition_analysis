import cv2
import json
import numpy as np
from ultralytics import YOLO
import time


class CameraDetector:
    def __init__(self, model_path='Data/models/yolov8n_weights/weights/best.pt', camera_index=0):
        """
        初始化目标检测器
        :param model_path: 训练好的YOLO模型路径
        :param camera_index: 摄像头设备索引
        """
        try:
            # 加载模型
            self.model = YOLO(model_path)
            self.names = self.model.names  # 获取类别名称映射

            # 初始化摄像头
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise RuntimeError("无法打开摄像头，请检查设备连接")

            # 测试读取一帧确保摄像头工作
            ret, test_frame = self.cap.read()
            if not ret:
                raise RuntimeError("摄像头初始化失败")

            print(f"目标检测器初始化成功！使用模型: {model_path}")
            print(f"可用类别: {list(self.names.values())}")

        except Exception as e:
            # 清理资源
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
            raise RuntimeError(f"初始化失败: {str(e)}")

    def get_camera_result(self):
        """
        获取当前摄像头帧的检测结果
        返回格式: JSON字符串 {标签1: 数量, 标签2: 数量, ...}
                 只包含数量大于0的标签
        """
        try:
            # 读取当前帧
            ret, frame = self.cap.read()
            if not ret:
                return json.dumps({"error": "摄像头读取失败"})

            # 执行目标检测
            results = self.model(frame, verbose=False)  # 禁用详细输出

            # 处理检测结果
            detections = {}
            for r in results:
                # 提取并处理检测到的类别
                classes = r.boxes.cls.cpu().numpy().astype(int)
                for class_id in classes:
                    label = self.names[class_id]
                    detections[label] = detections.get(label, 0) + 1

            # 只保留检测到的对象（数量>0）
            return json.dumps({k: v for k, v in detections.items() if v > 0}, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"检测过程中出错: {str(e)}"})

    def release_resources(self):
        """释放所有资源"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            print("摄像头资源已释放")
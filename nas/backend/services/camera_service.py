import cv2
import time
import threading
import logging

# 导入我们用于远程YOLO检测的模块
from .camera_detector import CameraDetector  
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CameraService:
    thread = None  # 用于运行摄像头捕获和处理循环的线程
    frame = None  # 最新处理后的视频帧（JPEG格式）
    last_access = 0  # 上次访问帧的时间戳

    # 私有变量，用于控制线程的生命周期
    _is_running = False
    _camera = None
    _detector = None  # CameraDetector 实例

    def __init__(self, server_ip='172.20.10.3', camera_index=0):
        self.server_ip = server_ip
        self.camera_index = camera_index
        logging.info(f"CameraService initialized with server_ip: {self.server_ip}, camera_index: {self.camera_index}")

    def _init_camera(self):

        if self._camera is None or not self._camera.isOpened():
            logging.info(f"正在尝试打开摄像头 (索引: {self.camera_index})...")
            # 尝试使用 cv2.CAP_V4L2 显式指定后端，提高兼容性
            # 或者直接 cap = cv2.VideoCapture(self.camera_index)
            self._camera = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
            if not self._camera.isOpened():
                logging.error(f"无法打开摄像头 {self.camera_index}。请检查摄像头是否连接正确或是否被其他程序占用。")
                self._camera = None
                return False
            # 尝试设置分辨率，这可以影响性能和图像质量
            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            logging.info("摄像头打开成功。")
            return True
        return True

    def _capture_and_process_frames(self):
        """
        主循环：捕获帧，发送到远程服务器处理，并更新本地缓存帧。
        """
        logging.info("摄像头捕获和处理线程已启动。")
        self._detector = CameraDetector(self.server_ip)  # 实例化远程检测器

        while self._is_running:
            if not self._init_camera():
                time.sleep(2)  # 如果摄像头未打开，等待一段时间后重试
                continue

            ret, frame = self._camera.read()
            if not ret:
                logging.warning("无法读取摄像头帧，跳过此帧。")
                time.sleep(0.1)  # 短暂等待
                continue

            # 将OpenCV BGR图像转换为JPEG字节流
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ret:
                logging.error("无法将帧编码为JPEG。")
                time.sleep(0.1)
                continue

            frame_bytes = buffer.tobytes()

            # 发送帧到远程YOLO服务器进行处理
            processed_frame_bytes, error_msg = self._detector.detect_and_get_frame(frame_bytes)

            if processed_frame_bytes:
                with threading.Lock():  # 使用锁确保线程安全更新共享资源
                    CameraService.frame = processed_frame_bytes
                    CameraService.last_access = time.time()
            else:
                logging.error(f"从YOLO服务器获取处理帧失败: {error_msg}")
                # 可以在这里选择是否显示原始帧或显示错误图像
                # 目前保持 frame 为上次成功获取的帧，或为None

            time.sleep(0.01)  # 控制循环速度，避免CPU占用过高

        if self._camera:
            self._camera.release()
            logging.info("摄像头已释放。")
        logging.info("摄像头捕获和处理线程已停止。")

    def start(self):
        if not self._is_running:
            self._is_running = True
            CameraService.thread = threading.Thread(target=self._capture_and_process_frames)
            CameraService.thread.daemon = True  # 将线程设置为守护线程，主程序退出时它也会退出
            CameraService.thread.start()
            logging.info("CameraService 线程已启动。")

    def stop(self):
        """
        停止摄像头服务。
        """
        if self._is_running:
            self._is_running = False
            if CameraService.thread:
                CameraService.thread.join(timeout=5)  # 等待线程结束，设置超时时间
                if CameraService.thread.is_alive():
                    logging.warning("摄像头服务线程未能正常停止。")
            logging.info("CameraService 线程停止请求已发送。")

    @classmethod
    def get_processed_frame(cls):

        with threading.Lock():
            return cls.frame

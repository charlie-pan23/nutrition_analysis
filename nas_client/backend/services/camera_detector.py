# camera_detector.py

import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CameraDetector:

    def __init__(self, server_ip):

        self.server_url = f"http://{server_ip}:5000/process_frame"
        logging.info(f"✨ YOLO服务器URL已设置为: {self.server_url}")

    def detect_and_get_frame(self, frame_bytes):
        if not frame_bytes:
            error_msg = "输入图像帧为空。"
            logging.error(f"{error_msg}")
            return None, error_msg

        try:
            # 使用 POST 请求将图像字节发送到服务器
            # headers 指定发送的是 JPEG 图像
            response = requests.post(
                self.server_url,
                data=frame_bytes,
                headers={'Content-Type': 'image/jpeg'},
                timeout=5  # 设置一个超时时间，避免因网络问题无限等待
            )
            response.raise_for_status()  # 检查HTTP响应状态码，如果不是200则抛出异常

            # 成功获取处理后的图像字节流
            processed_image_bytes = response.content
            return processed_image_bytes, None  # 返回处理后的图像字节和无错误

        except requests.exceptions.Timeout:
            error_msg = "请求远程YOLO服务器超时。请检查网络连接。"
            logging.error(f" {error_msg}")
            return None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = f"无法连接到YOLO服务器: {self.server_url}。请检查服务器是否运行、IP地址和端口是否正确以及防火墙设置。"
            logging.error(f" {error_msg}")
            return None, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"向YOLO服务器发送请求时发生未知错误: {e}"
            logging.error(f" {error_msg}", exc_info=True)
            return None, error_msg
        except Exception as e:
            error_msg = f"处理YOLO服务器响应时发生意外错误: {e}"
            logging.error(f" {error_msg}", exc_info=True)
            return None, error_msg

import json
import logging
import threading
import os
import time
import requests

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 文件路径定义
stage0_model = 'app/cache/stage/stage0.json'
stage1_model = 'app/cache/stage/stage1.json'
stage2_model = 'app/cache/stage/stage2.json'

# 发送目标地址
SEND_URL = "http://172.20.10.11:5000"
SEND_INTERVAL = 0.5  # 每秒发送 2 次

# 使用锁保证线程安全
data_lock = threading.Lock()

# 全局变量
data_to_send = None
stage = 0

class DataManager:
    def __init__(self):
        global data_to_send, stage
        with data_lock:
            data_to_send = self._load_cache(stage0_model)
            stage = data_to_send.get("stage", 0)

        # 启动定时发送线程
        self.sender_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.sender_thread.start()

    def _load_cache(self, filename: str) -> dict:
        """
        从 JSON 文件加载数据。
        :param filename: 缓存文件名。
        :return: 字典形式的数据，如果文件不存在或加载失败则返回空字典。
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logging.info(f"从 {filename} 加载缓存成功。")
                return data
            else:
                logging.warning(f"缓存文件 {filename} 不存在。")
                return {}
        except json.JSONDecodeError as e:
            logging.error(f"加载缓存文件 {filename} 失败，JSON 解析错误: {e}")
            return {}
        except Exception as e:
            logging.error(f"加载缓存文件 {filename} 时发生未知错误: {e}")
            return {}

    def _save_cache(self, filename: str, data: dict):
        """
        将数据保存到 JSON 文件。
        :param filename: 缓存文件名。
        :param data: 要保存的字典数据。
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.debug(f"数据已保存到 {filename}。")  # 使用debug级别，避免频繁输出
        except Exception as e:
            logging.error(f"保存缓存文件 {filename} 失败: {e}")

    def set_stage(self, new_stage: int):
        """
        设置当前阶段并更新 data_to_send。
        """
        global data_to_send, stage
        with data_lock:
            if new_stage == 0:
                data_to_send = self._load_cache(stage0_model)
            elif new_stage == 1:
                data_to_send = self._load_cache(stage1_model)
            elif new_stage == 2:
                data_to_send = self._load_cache(stage2_model)

            stage = new_stage
            self._update_time()

    def update_status(self, status: str):
        """
        更新 status 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send:
                data_to_send["status"] = status
                self._update_time()

    def _update_time(self):
        """
        更新 time 字段为当前时间戳。
        """
        global data_to_send
        if data_to_send:
            data_to_send["time"] = time.strftime("%Y-%m-%d %H:%M:%S")

    def set_db_connected(self, connected: bool):
        """
        更新数据库连接状态。
        """
        global data_to_send
        with data_lock:
            if "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["db_connected"] = connected
            self._update_time()

    def set_yolo_ready(self, ready: bool):
        """
        更新 YOLO 模型是否已加载完成的状态。
        """
        global data_to_send
        with data_lock:
            if "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["yolo_ready"] = ready
            self._update_time()

    def set_users(self, users: list):
        """
        设置 stage1 中的 users 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["users"] = users
                self._update_time()

    def set_updated(self, updated: bool):
        """
        设置 stage1 中的 updated 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["updated"] = updated
                self._update_time()

    def set_yolo_results(self, results: list):
        """
        设置 stage2 中的 yolo_results 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["yolo_results"] = results
                self._update_time()

    def set_meals(self, meals: list):
        """
        设置 stage2 中的 meals 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["meals"] = meals
                self._update_time()

    def set_meals_updated(self, meals_updated: bool):
        """
        设置 stage2 中的 meals_updated 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["meals_updated"] = meals_updated
                self._update_time()

    def set_workflow_status(self, status: str):
        """
        设置 stage2 中的 workflow_status 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["workflow_status"] = status
                self._update_time()

    def set_workflow_response(self, response: str):
        """
        设置 stage2 中的 workflow_response 字段。
        """
        global data_to_send
        with data_lock:
            if data_to_send and "data" in data_to_send and isinstance(data_to_send["data"], dict):
                data_to_send["data"]["workflow_response"] = response
                self._update_time()

    def get_data_to_send(self):
        """
        获取当前 data_to_send 的副本（线程安全）
        """
        with data_lock:
            return data_to_send.copy() if data_to_send else {}

    def _send_loop(self):
        """
        循环发送 data_to_send 到指定 URL
        """
        while True:
            try:
                data = self.get_data_to_send()
                if data:
                    requests.post(SEND_URL, json=data, timeout=1)
                    logging.debug("已异步发送 data_to_send")
            except Exception as e:
                logging.error(f"发送 data_to_send 失败: {e}")
            time.sleep(SEND_INTERVAL)

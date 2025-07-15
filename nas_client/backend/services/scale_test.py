import random
import time

class ScaleService:
    def __init__(self):
        self.weight = 0.0
        self.last_update = 0
        self.active = False

    def start(self):
        self.active = True
        self.weight = 0.0
        self.last_update = time.time()

    def stop(self):
        self.active = False

    def get_weight(self):
        if not self.active:
            print("Scale is not running")
            return 0.0

        # 返回随机的称重数值
        current_time = time.time()
        if current_time - self.last_update > 1.0:
            self.weight = random.uniform(100, 1500)
            self.last_update = current_time

        return self.weight
    def is_running(self):
        """返回当前称重模块是否处于运行状态"""
        return self.active
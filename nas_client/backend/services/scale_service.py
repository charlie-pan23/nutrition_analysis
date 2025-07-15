import time
import RPi.GPIO as GPIO
from backend.hx711 import HX711


class ScaleService:
    def __init__(self):
        self.weight = 0.0
        self.active = False
        self.hx = None
        self.reference_unit = 425  # 根据你的校准值修改
        self.dt_pin = 5  # DT引脚连接的GPIO编号
        self.sck_pin = 6  # SCK引脚连接的GPIO编号

    def start(self):
        """初始化并启动HX711称重模块"""
        if self.active:
            return

        # 设置GPIO模式
        GPIO.setmode(GPIO.BCM)

        # 创建HX711实例
        self.hx = HX711(dt=self.dt_pin, sck=self.sck_pin)

        try:
            # 配置HX711
            self.hx.set_reading_format("MSB", "MSB")
            self.hx.set_reference_unit(self.reference_unit)
            self.hx.reset()
            self.hx.tare()  # 去皮归零
            print("去皮完成！现在可以放置物体进行称重...")
            self.active = True
        except Exception as e:
            print(f"初始化HX711失败: {e}")
            self.stop()

    def stop(self):
        """停止并清理资源"""
        self.active = False
        if self.hx:
            self.hx.power_down()
            self.hx.power_up()
            self.hx = None
        GPIO.cleanup()
        print("GPIO已清理，称重模块已关闭")

    def get_weight(self):
        """获取当前重量（单位：克）"""
        if not self.active:
            return 0.0

        try:
            # 获取5次读数取平均，并转为整数
            val = int(abs(self.hx.get_weight(5)))
            self.weight = val
        except Exception as e:
            print(f"读取称重数据失败: {e}")
            self.weight = 0.0

        return self.weight

    def main_loop(self):
        """主循环函数，持续进行称重并在控制台打印结果"""
        self.start()
        try:
            while True:
                weight = self.get_weight()
                print(f"当前重量: {weight} 克")
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("程序正在退出...")
        finally:
            self.stop()
    def is_running(self):
        """返回当前称重模块是否处于运行状态"""
        return self.active
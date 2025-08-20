import time
import RPi.GPIO as GPIO
# 你的路径可能是 from hx711 import HX711
# 或者像你app.py里写的 from backend.hx711 import HX711
# 请确保这里的导入路径正确，和你的文件结构一致
from hx711 import HX711 
import atexit # 导入 atexit 用于程序退出时的清理

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ScaleService:
    def __init__(self):
        self.weight = 0.0
        self.active = False
        self.hx = None
        self.reference_unit = 436.538  # 根据你的校准值修改
        self.dt_pin = 5            # DT引脚连接的GPIO编号
        self.sck_pin = 6           # SCK引脚连接的GPIO编号

        # 在类的初始化时设置GPIO模式，这通常只做一次
        try:
            GPIO.setmode(GPIO.BCM)
            # logging.error("GPIO模式已设置为BCM。") # 调试用
        except RuntimeWarning:
            # logging.error("GPIO模式已设置过。") # 调试用
            pass # 忽略重复设置GPIO模式的警告

    def start(self):
        """初始化并启动HX711称重模块"""
        if self.active and self.hx is not None:
            logging.error("称重服务已在运行且HX711已初始化，无需重复启动。")
            return True

        logging.error("正在启动称重服务并初始化HX711...")
        try:
            # 如果HX711实例已经存在，尝试对其进行清理或唤醒
            if self.hx:
                try:
                    self.hx.power_up() # 如果之前被power_down，这里需要重新供电
                except Exception as e:
                    logging.error(f"HX711 power_up 失败: {e}，尝试重新创建实例。")
                    self.hx = None # 确保实例无效，以便重新创建

            # ** 核心修正：严格按照你原始能工作的代码格式创建 HX711 实例 **
            if self.hx is None: # 只有当HX711实例不存在时才创建
                self.hx = HX711(self.dt_pin, self.sck_pin)

            # 配置HX711
            # ** 核心修正：恢复 set_reading_format，因为它在你原始代码中存在 **
            self.hx.set_reading_format("MSB", "MSB") 
            
            self.hx.set_reference_unit(self.reference_unit)
            self.hx.reset()
            self.hx.tare()  # 去皮归零
            logging.error("HX711初始化完成并已去皮！现在可以放置物体进行称重...")
            self.active = True
            return True
        except Exception as e:
            logging.error(f"初始化HX711失败: {e}")
            self.stop() # 初始化失败也调用 stop 进行清理
            self.active = False
            self.hx = None
            return False

    def stop(self):
        """停止并清理资源"""
        if not self.active and self.hx is None:
            logging.error("称重服务未运行或未初始化，无需停止。")
            return

        logging.error("正在停止称重服务并清理GPIO...")
        self.active = False
        if self.hx:
            try:
                self.hx.power_down() # 安全地关闭HX711模块电源
                logging.error("HX711模块已断电。")
            except Exception as e:
                logging.error(f"关闭HX711电源时发生错误: {e}")
            # ** 核心修正：确保这里移除了 self.hx.power_up() **
            self.hx = None # 释放HX711实例

        try:
            GPIO.cleanup() # 清理所有GPIO引脚
            logging.error("GPIO已清理。")
        except Exception as e:
            logging.error(f"清理GPIO时发生错误: {e}")

    def get_weight(self):
        """获取当前重量（单位：克）"""
        if not self.active or self.hx is None:
            # 如果服务未激活或HX711实例不存在，返回0.0
            logging.error("Scale is not running")
            return 0.0

        try:
            # 获取5次读数取平均，并转为整数
            val = int(abs(self.hx.get_weight(5)))
            logging.error("val===")
            logging.error(val)
            self.weight = float(val) # 存储为浮点数
        except Exception as e:
            logging.error(f"读取称重数据失败: {e}，返回0.0。")
            logging.error("读取称重数据失败")
            self.weight = 0.0

        logging.error("成功===")
        logging.error(self.weight)
        return self.weight

    def main_loop(self):
        """主循环函数，持续进行称重并在控制台打印结果"""
        if not self.start():
            logging.error("无法启动称重服务，退出主循环。")
            return

        logging.error("进入称重主循环 (用于独立测试) ...")
        try:
            while self.active: # 循环由 self.active 控制
                weight = self.get_weight()
                logging.error(f"当前重量: {weight} 克")
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logging.error("\n程序正在退出...")
        except Exception as e:
            logging.error(f"主循环中发生意外错误: {e}")
        finally:
            self.stop() # 确保在退出时停止并清理

# --- 模块级清理（确保在Python脚本完全退出时执行） ---
def _module_cleanup():
    # 尝试安全关闭HX711，避免在程序异常退出时GPIO保持不当状态
    try:
        # 创建一个临时实例来调用stop()，但要避免在__init__中再次遇到初始化错误
        # 这里的清理是一个最佳努力的尝试，主要确保GPIO.cleanup()被调用
        temp_scale_service = ScaleService()
        temp_scale_service.active = True # 假设它曾经活跃
        # 不尝试创建HX711实例，直接调用stop()，让它清理GPIO
        temp_scale_service.hx = None # 确保hx是None，防止stop()尝试对一个不存在的hx操作
        temp_scale_service.stop()
    except Exception as e:
        logging.error(f"HX711服务模块级清理时发生错误: {e}")
    finally:
        # 无论如何都尝试清理GPIO，这是最关键的
        try:
            GPIO.cleanup()
            logging.error("GPIO引脚在模块退出时已确保清理。")
        except Exception as e:
            logging.error(f"最终GPIO清理时发生错误: {e}")

atexit.register(_module_cleanup)

# --- 示例：独立测试此模块 ---
if __name__ == '__main__':
    logging.error("--- 独立电子秤服务测试 ---")
    test_scale_service = ScaleService()
    test_scale_service.main_loop()
    logging.error("--- 独立电子秤服务测试结束 ---")

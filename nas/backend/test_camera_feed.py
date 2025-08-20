import cv2
import sys
import logging
import time # 导入 time 模块用于延时和生成文件名

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_camera_feed_to_file(camera_index=0, width=640, height=480, num_frames=5):
    """
    捕获指定数量的摄像头帧并保存为JPEG文件，不显示图形界面。
    
    参数:
        camera_index (int): 摄像头设备索引，通常是 0。
        width (int): 设置捕获帧的宽度。
        height (int): 设置捕获帧的高度。
        num_frames (int): 要捕获并保存的帧数。
    """
    logging.info(f"正在尝试打开摄像头 (索引: {camera_index}, 分辨率: {width}x{height})...")

    cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

    if not cap.isOpened():
        logging.error(f"错误: 无法打开摄像头 {camera_index}。请检查摄像头是否连接正确或是否被其他程序占用。")
        logging.error("如果您看到 'can't open camera by index' 警告，请确保没有其他程序占用摄像头。")
        logging.error("尝试重启树莓派，或使用 'sudo lsof /dev/video0' 查找占用进程。")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    fourcc = cv2.VideoWriter_fourcc('Y','U','Y','V')
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)

    logging.info(f"摄像头打开成功。将捕获 {num_frames} 帧并保存到当前目录。")

    frames_captured = 0
    while frames_captured < num_frames:
        ret, frame = cap.read()

        if not ret:
            logging.warning("无法读取摄像头帧，可能流已结束或摄像头断开。")
            break

        # 生成带有时间戳的文件名，避免覆盖
        timestamp = int(time.time())
        filename = f"camera_test_frame_{timestamp}_{frames_captured}.jpg"
        
        # 将帧保存为JPEG文件
        cv2.imwrite(filename, frame)
        logging.info(f"帧 {frames_captured+1}/{num_frames} 已保存为 {filename}")
        
        frames_captured += 1
        time.sleep(1) # 每隔1秒捕获一帧，避免太快

    cap.release()
    logging.info("摄像头已释放，图像保存测试结束。")

if __name__ == "__main__":
    # 确保在运行前，没有其他程序占用 /dev/video0
    # 默认捕获 5 帧，分辨率 640x480
    test_camera_feed_to_file(camera_index=0, width=640, height=480, num_frames=5)

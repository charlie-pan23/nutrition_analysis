import os
import cv2
import numpy as np
from ultralytics import YOLO


def validate_model(model_path):
    print(f"验证模型: {model_path}")

    # 检查文件是否存在
    if not os.path.exists(model_path):
        print("错误: 模型文件不存在")
        return False

    # 检查文件大小
    file_size = os.path.getsize(model_path)
    print(f"模型文件大小: {file_size} 字节")

    # 尝试加载模型
    try:
        print("加载模型...")
        model = YOLO(model_path)
        print("模型加载成功")

        # 创建测试图像
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_img, "Test Image", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 运行推理
        results = model(test_img)

        print("推理结果:")
        for result in results:
            print(f"- {len(result.boxes)} 个检测对象")

        return True
    except Exception as e:
        print(f"模型验证失败: {str(e)}")
        return False


if __name__ == "__main__":
    model_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "runs", "yolov8n_weights", "weights", "best.pt"
    )
    success = validate_model(model_path)
    print(f"模型验证 {'成功' if success else '失败'}")
import cv2
from ultralytics import YOLO
from food_properties import FOOD_DENSITY, FOOD_AVG_HEIGHT
import torch



torch.set_num_threads(2)
# --- 配置 ---
# !!! 关键：加载你微调好的模型 !!!
MODEL_PATH = 'runs/yolov8n_weights/weights/best.pt' #<-- 检查并修改为你的实际路径

# !!! 关键：手动标定 !!!
# 放置一个已知尺寸的物体（如一元硬币，直径2.5cm），测量其像素宽度，然后计算：像素宽度 / 2.5
PIXELS_PER_CM = 40.0 

try:
    model = YOLO(MODEL_PATH)
    class_names = model.names
except Exception as e:
    print(f"Loading model failed: {e}\nplease make sure the path to the model file '{MODEL_PATH}' is correct.")
    exit()

def estimate_weight(class_name, box_w, box_h):
    if class_name not in FOOD_DENSITY or class_name not in FOOD_AVG_HEIGHT: return None
    real_w_cm = box_w / PIXELS_PER_CM
    real_h_cm = box_h / PIXELS_PER_CM
    area = real_w_cm * real_h_cm
    volume = area * FOOD_AVG_HEIGHT[class_name]
    weight = volume * FOOD_DENSITY[class_name]
    return round(weight, 1)

cap = cv2.VideoCapture(0)
while True:
    success, frame = cap.read()
    if not success: break
    results = model(frame, stream=True, verbose=False)
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf, cls_id = float(box.conf[0]), int(box.cls[0])
            class_name = class_names[cls_id]
            if conf > 0.45:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                weight = estimate_weight(class_name, x2 - x1, y2 - y1)
                label = f"{class_name}: {weight}g" if weight is not None else class_name
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Live Food Detection & Weight Estimation", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
cap.release()
cv2.destroyAllWindows()

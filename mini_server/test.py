img_np_rgb, error_msg = process_image_for_yolo(open('test.png', 'rb').read())

print("11======")
print(img_np_rgb)
print("======")
print(error_msg)
# 执行YOLOv8推理
results = model.predict(img_np_rgb, verbose=False)

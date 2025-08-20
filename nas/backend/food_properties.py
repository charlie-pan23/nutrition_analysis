# 食物密度 (单位: g/cm^3)
# !!! 这里的 key 必须和你 .yaml 文件中的 names 列表一致 !!!
FOOD_DENSITY = {
    "apple": 0.609, "banana": 0.95, "cake": 0.4, "carrot": 0.6,
    "donut": 0.45, "hot_dog": 0.9, "orange": 0.75, "pizza": 0.5,
    "sandwich": 0.45, "sushi": 1.1
    # 如果你的数据集生成了其他类别，请在这里添加
}

# 估算的食物平均高度 (单位: cm)
FOOD_AVG_HEIGHT = {
    "apple": 7.0, "banana": 3.0, "cake": 6.0, "carrot": 2.5,
    "donut": 3.5, "hot_dog": 2.5, "orange": 8.0, "pizza": 1.5,
    "sandwich": 5.0, "sushi": 2.5
    # 如果你的数据集生成了其他类别，请在这里添加
}
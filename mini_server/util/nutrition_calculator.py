# utils/nutrition_utils.py

class NutritionCalculator:
    """
    营养计算工具类
    使用 Mifflin-St Jeor 公式计算每日总能量消耗(TDEE)
    并提供三大营养素分配建议
    """

    # 活动因子映射表 (基于活动水平)
    ACTIVITY_FACTORS = {
        1: 1.2,  # 久坐（很少或没有运动）
        2: 1.375,  # 轻度活动（轻度运动/运动1-3天/周）
        3: 1.55,  # 中度活动（中等运动/运动3-5天/周）
        4: 1.725,  # 非常活跃（高强度运动/运动6-7天/周）
        5: 1.9  # 极其活跃（非常高强度运动/体力工作/训练2次/天）
    }

    # 营养分配比例 (蛋白质/脂肪/碳水)
    NUTRIENT_RATIOS = {
        # (蛋白质比例, 脂肪比例, 碳水比例)
        "balanced": (0.25, 0.25, 0.50),  # 均衡饮食
        "low_carb": (0.35, 0.40, 0.25),  # 低碳水饮食
        "high_protein": (0.40, 0.30, 0.30)  # 高蛋白饮食
    }

    # 宏量营养素热值 (千卡/克)
    CAL_PER_PROTEIN = 4
    CAL_PER_FAT = 9
    CAL_PER_CARB = 4

    @classmethod
    def calculate_bmr(cls, gender, age, height_cm, weight_kg):
        """
        使用 Mifflin-St Jeor 公式计算基础代谢率(BMR)

        参数:
        - gender: 'male' 或 'female'
        - age: 年龄(岁)
        - height_cm: 身高(厘米)
        - weight_kg: 体重(千克)

        返回:
        - BMR (基础代谢率，单位: 千卡/天)
        """
        if gender.lower() == 'male':
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        elif gender.lower() == 'female':
            return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            raise ValueError("无效性别，请输入 'male' 或 'female'")

    @classmethod
    def calculate_tdee(cls, bmr, activity_level):
        """
        计算每日总能量消耗(TDEE)

        参数:
        - bmr: 基础代谢率
        - activity_level: 活动水平 (1-5)

        返回:
        - TDEE (每日总能量消耗，单位: 千卡/天)
        """
        factor = cls.ACTIVITY_FACTORS.get(int(activity_level), 1.2)
        return bmr * factor

    @classmethod
    def calculate_macronutrients(cls, tdee, diet_type="balanced"):
        """
        计算三大营养素目标摄入量(克)

        参数:
        - tdee: 每日总能量消耗
        - diet_type: 饮食类型 ('balanced', 'low_carb', 'high_protein')

        返回:
        - 元组 (protein_g, fat_g, carb_g) 目标蛋白质/脂肪/碳水(克)
        """
        ratios = cls.NUTRIENT_RATIOS.get(diet_type, cls.NUTRIENT_RATIOS["balanced"])
        protein_ratio, fat_ratio, carb_ratio = ratios

        # 计算各营养素提供的热量(千卡)
        protein_cals = tdee * protein_ratio
        fat_cals = tdee * fat_ratio
        carb_cals = tdee * carb_ratio

        # 计算对应克数
        protein_g = protein_cals / cls.CAL_PER_PROTEIN
        fat_g = fat_cals / cls.CAL_PER_FAT
        carb_g = carb_cals / cls.CAL_PER_CARB

        return round(protein_g), round(fat_g), round(carb_g)

    @classmethod
    def calculate_daily_goals(cls, gender, age, height_cm, weight_kg, activity_level, diet_type="balanced"):
        """
        计算完整每日营养目标

        参数:
        - gender: 'male' 或 'female'
        - age: 年龄(岁)
        - height_cm: 身高(厘米)
        - weight_kg: 体重(千克)
        - activity_level: 活动水平 (1-5)
        - diet_type: 饮食类型 ('balanced', 'low_carb', 'high_protein')

        返回:
        - 字典 {
            "tdee": TDEE值(千卡),
            "protein": 蛋白质目标(克),
            "fat": 脂肪目标(克),
            "carb": 碳水目标(克),
            "ratio": 营养素比例字符串
        }
        """
        if not (1 <= activity_level <= 5):
            raise ValueError("活动水平必须为1-5之间的整数")

        bmr = cls.calculate_bmr(gender, age, height_cm, weight_kg)
        tdee = cls.calculate_tdee(bmr, activity_level)
        protein_g, fat_g, carb_g = cls.calculate_macronutrients(tdee, diet_type)

        return {
            "tdee": round(tdee),
            "protein": protein_g,
            "fat": fat_g,
            "carb": carb_g,
            "ratio": f"{cls.NUTRIENT_RATIOS[diet_type][0] * 100}%P/{cls.NUTRIENT_RATIOS[diet_type][1] * 100}%F/{cls.NUTRIENT_RATIOS[diet_type][2] * 100}%C"
        }


# 使用示例
if __name__ == "__main__":
    # 计算示例 (30岁男性，180cm，75kg，中度活动，均衡饮食)
    result = NutritionCalculator.calculate_daily_goals(
        gender="male",
        age=21,
        height_cm=172,
        weight_kg=72,
        activity_level=4,
        diet_type="low_carb"
    )

    print("每日营养目标:")
    print(f"总热量: {result['tdee']} kcal")
    print(f"蛋白质: {result['protein']}g")
    print(f"脂肪: {result['fat']}g")
    print(f"碳水: {result['carb']}g")
    print(f"营养素比例: {result['ratio']}")
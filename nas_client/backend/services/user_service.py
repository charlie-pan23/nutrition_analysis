# services/user_service.py
import os
import json
import uuid
import time

USER_DB_FILE = "Data/users.json"


class UserService:
    def __init__(self):
        self.users_db = self.load_users()

    def load_users(self):
        """加载用户数据"""
        if not os.path.exists(USER_DB_FILE):
            initial_data = {
                "users": [
                    {"openid": "oJ2D36_6Gn1roXODNbHPy9SYgAVs", "name": "Admin", "role": "admin"}
                ],
                "metadata": {
                    # 可以从其他地方读取或初始化 metadata
                    "conditionOptions": [],
                    "avoidanceOptions": [],
                    "preferenceOptions": []
                }
            }
            self.save_users(initial_data["users"])
            return initial_data["users"]

        try:
            with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("users", [])  # 只取 users 字段
        except (FileNotFoundError, json.JSONDecodeError):
            print("用户数据库损坏，创建新的数据库")
            return []

    def save_users(self, users):
        """保存用户数据，确保不更改users.json的格式"""
        with open(USER_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return users

    def get_all_users(self):
        """获取所有用户（可包含部分额外信息）"""
        return [
            {
                "openid": u["openid"],
                "nickname": u["nickname"],
                "gender": u["gender"],
                "height": u["height"],
                "weight": u["weight"],
                "age": u["age"],
                "preferences": u["preferences"],
                "allergies": u["allergies"],
                "diseases": u["diseases"],
                "activity_level": u["activity_level"],
                "daily_energy_kcal": u["daily_energy_kcal"],
                "daily_carbohydrates_g": u["daily_carbohydrates_g"],
                "daily_fat_g": u["daily_fat_g"],
                "daily_protein_g": u["daily_protein_g"]
            }
            for u in self.users_db
        ]

    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        return next((u for u in self.users_db if u["id"] == user_id), None)

    def get_user_by_name(self, name):
        """根据用户名获取用户"""
        return next((u for u in self.users_db if u["name"] == name), None)

    def create_user(self, nickname, age=None, height=None, weight=None, diseases=None, allergies=None,
                    preferences=None):
        """创建新用户，支持更多字段"""
        if any(u["name"] == nickname for u in self.users_db):
            raise ValueError("用户名已存在")
        new_user = {
            "openid": str(uuid.uuid4()),
            "nickname": nickname,
            "age": age,
            "height": height,
            "weight": weight,
            "allergies": allergies or [],
            "diseases": diseases or [],
            "preferences": preferences or [],
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")  # 使用 ISO 格式
        }

        self.users_db.append(new_user)
        self.save_users(self.users_db)
        return new_user

    def delete_user(self, user_id):
        """删除用户"""
        user_index = next((i for i, u in enumerate(self.users_db) if u["openid"] == user_id), None)
        if user_index is None:
            raise ValueError("用户不存在")

        deleted_user = self.users_db.pop(user_index)
        self.save_users(self.users_db)
        return deleted_user

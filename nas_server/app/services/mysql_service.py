import logging
import mysql.connector
import threading
import time
from datetime import datetime

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MySQLService:
    def __init__(self, db_config: dict, server_data_manager):
        """
        初始化 MySQL 服务。
        :param db_config: 包含数据库连接参数的字典 (host, port, user, password, database)。
        :param server_data_manager: ServerDataManager 的实例，用于更新服务器状态。
        """
        self.db_config = db_config
        self.server_data_manager = server_data_manager
        self._connection = None
        self._connection_lock = threading.Lock() # 用于保护连接对象的锁
        self._is_connected = False # 内部连接状态标记

    def _initialize_connection(self):
        """
        私有方法：尝试建立 MySQL 数据库连接。
        此方法在单独的线程中调用，以避免阻塞主线程。
        连接成功或失败后会更新 server_data_manager 中的数据库状态。
        """
        with self._connection_lock:
            if self._is_connected:
                logging.info("MySQL连接已存在且活跃，无需重复连接。")
                self.server_data_manager.set_db_connected(True)
                return

            logging.info(f"正在尝试连接 MySQL 数据库 (host: {self.db_config.get('host', 'N/A')}, port: {self.db_config.get('port', 'N/A')}, user: {self.db_config.get('user', 'N/A')})...")
            try:
                # 尝试连接到数据库
                conn = mysql.connector.connect(
                    host=self.db_config.get('host'),
                    port=self.db_config.get('port'),
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password')
                    # database=self.db_config.get('database') # 如果需要连接特定数据库，可以在此处添加
                )
                if conn.is_connected():
                    self._connection = conn
                    self._is_connected = True
                    self.server_data_manager.set_db_connected(True)
                    logging.info("MySQL 数据库连接成功！")
                else:
                    self._connection = None
                    self._is_connected = False
                    self.server_data_manager.set_db_connected(False)
                    logging.error("MySQL 数据库连接失败：连接未建立。")

            except mysql.connector.Error as err:
                self._connection = None
                self._is_connected = False
                self.server_data_manager.set_db_connected(False)
                if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                    logging.critical("MySQL 数据库连接失败：访问被拒绝，可能是用户名或密码错误。")
                elif err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                    logging.critical(f"MySQL 数据库连接失败：无法连接到主机 {self.db_config.get('host', 'N/A')}:{self.db_config.get('port', 'N/A')}。请检查 MySQL 服务是否运行，网络是否可达，防火墙是否阻挡。")
                else:
                    logging.critical(f"MySQL 数据库连接失败：发生未知错误：{err}")
            except Exception as e:
                self._connection = None
                self._is_connected = False
                self.server_data_manager.set_db_connected(False)
                logging.critical(f"初始化 MySQL 连接时发生意外错误: {e}", exc_info=True)

    def start_connection_in_thread(self):
        """在独立线程中启动 MySQL 数据库的异步连接。"""
        logging.info("启动 MySQL 数据库连接异步线程。")
        db_thread = threading.Thread(target=self._initialize_connection, daemon=True)
        db_thread.start()

    def is_connected(self) -> bool:
        """
        检查数据库连接是否活跃。
        如果连接已断开，会尝试重新连接。
        """
        with self._connection_lock:
            if self._connection:
                try:
                    # 尝试执行一个轻量级操作来检查连接活跃性
                    self._connection.ping(reconnect=True, attempts=1)
                    if self._connection.is_connected():
                        if not self._is_connected: # 如果之前标记为断开，现在恢复了，更新状态
                            self._is_connected = True
                            self.server_data_manager.set_db_connected(True)
                            logging.info("MySQL连接已恢复活跃。")
                        return True
                    else:
                        logging.warning("MySQL连接已断开，尝试重新建立连接。")
                        self._is_connected = False
                        self.server_data_manager.set_db_connected(False)
                        self._connection.close() # 关闭旧的无效连接
                        self._connection = None
                        self._initialize_connection() # 尝试重新连接
                        return self._is_connected # 返回重新连接后的状态
                except mysql.connector.Error as e:
                    logging.error(f"MySQL连接 ping 失败: {e}，尝试重新连接。")
                    self._is_connected = False
                    self.server_data_manager.set_db_connected(False)
                    if self._connection:
                        self._connection.close()
                    self._connection = None
                    self._initialize_connection() # 尝试重新连接
                    return self._is_connected # 返回重新连接后的状态
            else:
                # 如果_connection为None，说明从未成功连接或已关闭
                if not self._is_connected: # 避免重复日志，仅当标记为非连接时才尝试
                    logging.warning("MySQL连接对象为空或未连接，尝试建立新连接。")
                    self._initialize_connection() # 尝试建立新连接
                return self._is_connected # 返回尝试连接后的状态

    def get_connection(self):
        """
        获取当前活跃的数据库连接对象。
        外部模块可以通过这个方法获取连接来执行复杂查询，但应注意线程安全和连接管理。
        通常，更好的做法是让服务类内部提供执行查询的方法。
        """
        with self._connection_lock:
            if self.is_connected():
                return self._connection
            return None

    def execute_query(self, query: str, params: tuple = None, fetch_one=False, fetch_all=False):
        """
        执行数据库查询（INSERT, UPDATE, DELETE, SELECT）。
        :param query: SQL 查询字符串。
        :param params: 查询参数元组。
        :param fetch_one: 如果是 SELECT 查询，是否只获取一条结果。
        :param fetch_all: 如果是 SELECT 查询，是否获取所有结果。
        :return: SELECT 查询的结果，或非 SELECT 查询的 None。
        """
        with self._connection_lock:
            if not self.is_connected():
                logging.error("数据库未连接，无法执行查询。")
                return None

            cursor = None
            try:
                cursor = self._connection.cursor(buffered=True) # 使用 buffered=True 避免操作冲突
                cursor.execute(query, params or ())
                self._connection.commit() # 提交非SELECT操作

                if query.strip().upper().startswith("SELECT"):
                    if fetch_one:
                        return cursor.fetchone()
                    elif fetch_all:
                        return cursor.fetchall()
                return None # 非 SELECT 查询不返回数据

            except mysql.connector.Error as err:
                logging.error(f"执行数据库查询失败: {err}", exc_info=True)
                self._connection.rollback() # 回滚事务
                return None
            finally:
                if cursor:
                    cursor.close()
                # 注意：这里不关闭 self._connection，因为它是长期持有的服务连接

    def add_user(self, nickname, openid, height=None, weight=None, age=None, gender=None, preferences=None,
                 allergies=None, diseases=None, activity_level='lightly_active', last_login_at=None,
                 daily_energy_kcal=0.00, daily_carbohydrates_g=0.00, daily_fat_g=0.00, daily_protein_g=0.00):
        """
        Insert a new user into the users table. Timestamps (created_at, updated_at) are handled automatically by the DB.
        """
        query = """
                INSERT INTO users (nickname, openid, height, weight, age, gender, preferences, allergies, diseases, \
                                   activity_level, last_login_at, daily_energy_kcal, daily_carbohydrates_g, daily_fat_g, \
                                   daily_protein_g)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                """
        params = (nickname, openid, height, weight, age, gender, preferences, allergies, diseases, activity_level,
                  last_login_at, daily_energy_kcal, daily_carbohydrates_g, daily_fat_g, daily_protein_g)
        return self.execute_query(query, params)

    def delete_user(self, openid):
        """
        Delete a user by openid.
        """
        query = "DELETE FROM users WHERE openid = %s"
        params = (openid,)
        return self.execute_query(query, params)

    def update_user(self, openid, nickname=None, height=None, weight=None, age=None, gender=None, preferences=None,
                    allergies=None, diseases=None, activity_level=None, last_login_at=None, daily_energy_kcal=None,
                    daily_carbohydrates_g=None, daily_fat_g=None, daily_protein_g=None):
        """
        Update user fields by openid (all except openid). Only provided fields are updated.
        Timestamps (created_at, updated_at) are handled automatically by the DB.
        """
        set_clause = []
        params = []
        if nickname is not None:
            set_clause.append("nickname = %s")
            params.append(nickname)
        if height is not None:
            set_clause.append("height = %s")
            params.append(height)
        if weight is not None:
            set_clause.append("weight = %s")
            params.append(weight)
        if age is not None:
            set_clause.append("age = %s")
            params.append(age)
        if gender is not None:
            set_clause.append("gender = %s")
            params.append(gender)
        if preferences is not None:
            set_clause.append("preferences = %s")
            params.append(preferences)
        if allergies is not None:
            set_clause.append("allergies = %s")
            params.append(allergies)
        if diseases is not None:
            set_clause.append("diseases = %s")
            params.append(diseases)
        if activity_level is not None:
            set_clause.append("activity_level = %s")
            params.append(activity_level)
        if last_login_at is not None:
            set_clause.append("last_login_at = %s")
            params.append(last_login_at)
        if daily_energy_kcal is not None:
            set_clause.append("daily_energy_kcal = %s")
            params.append(daily_energy_kcal)
        if daily_carbohydrates_g is not None:
            set_clause.append("daily_carbohydrates_g = %s")
            params.append(daily_carbohydrates_g)
        if daily_fat_g is not None:
            set_clause.append("daily_fat_g = %s")
            params.append(daily_fat_g)
        if daily_protein_g is not None:
            set_clause.append("daily_protein_g = %s")
            params.append(daily_protein_g)

        if not set_clause:
            return None  # Nothing to update

        set_clause_str = ", ".join(set_clause)
        query = f"UPDATE users SET {set_clause_str} WHERE openid = %s"
        params.append(openid)
        return self.execute_query(query, tuple(params))

    def get_user_by_openid(self, openid):
        """
        Fetch user details by openid.
        """
        query = "SELECT * FROM users WHERE openid = %s"
        params = (openid,)
        return self.execute_query(query, params, fetch_one=True)

    def get_all_users(self):
        query = "SELECT * FROM users"
        result = self.execute_query(query, fetch_all=True)

        if not result:
            logging.info("未查询到任何用户记录。")
            return {"user": []}

        # 获取列名
        with self._connection_lock:
            if not self.is_connected():
                logging.error("数据库未连接，无法获取列信息。")
                return {"user": []}

            cursor = self._connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            cursor.close()

        # 定义需要转换为字符串的时间字段和 JSON 字段
        datetime_fields = ['created_at', 'updated_at', 'last_login_at']
        json_fields = ['preferences', 'allergies', 'diseases']
        enum_fields = {
            'gender': ['男', '女', '其他'],
            'activity_level': ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active']
        }

        # 构建结果
        users = []
        for row in result:
            user = {}
            for col, value in zip(columns, row):
                if col in datetime_fields and isinstance(value, datetime):
                    # 时间字段转为标准格式字符串
                    user[col] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif col in json_fields and isinstance(value, str):
                    # JSON 字符串字段保留为字符串，或可选 json.loads(value)
                    user[col] = value  # 或 json.loads(value) 如果需要转为 dict
                elif col in enum_fields and value is not None:
                    # 枚举字段保留原值（如 '男' 或 'lightly_active'）
                    user[col] = value
                else:
                    # 其他字段直接赋值
                    user[col] = value
            users.append(user)

        logging.info(f"成功查询到 {len(users)} 条用户记录。")
        return {"user": users}


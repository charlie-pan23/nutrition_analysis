import os
import requests
from flask import Flask
import logging

from flask_sqlalchemy import SQLAlchemy

from demo.user_service import User, get_user_by_openid

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)

# 从环境变量获取数据库连接URI，提高安全性与可配置性
# 格式：mysql+pymysql://用户名:密码@主机名:端口/数据库名
# ⚠️ 注意：生产环境中，请务必使用环境变量来管理敏感信息！
# 例如： export DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/nas"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:123456@localhost:3306/nas' # 默认值，仅供开发测试，请勿用于生产！
)
# 关闭SQLAlchemy事件系统，减少不必要的内存开销和信号发送
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
@app.route('/wx_login/<code>', methods=['GET'])
def wx_login(code):
    appid = 'wxf07a5d5ce93485ad'
    secret = '0dba341f543a35cd764eddcd120d864e'
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    response = requests.get(url)
    logger.info("微信登录接口启动成功")
    logger.info(f"微信登录接口返回结果：{response.json()}")
    # 第一步：根据openid判断用户是否存在
    # 第二步：如果用户不存在，返回用户列表，让小程序端选中，去绑定用户
    # 第三步：如果用户存在，直接登录
    user = get_user_by_openid(response.json()['openid'])
    return user.to_dict()

# --- 5. 应用运行入口 ---
if __name__ == '__main__':
    logger.info("Flask 应用启动中...")
    app.run(host='0.0.0.0', port=6200, debug=True, threaded=True)

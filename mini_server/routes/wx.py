import logging
from datetime import datetime

import requests
from flask import jsonify

from service.user_service import get_user_by_openid, update_user, get_all_users

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from flask import Blueprint

wx_bp = Blueprint('wx', __name__)

# --- user ---
@wx_bp.route('/wx_login/<code>', methods=['GET'])
def wx_login(code):
    appid = 'wxf07a5d5ce93485ad'
    secret = '0dba341f543a35cd764eddcd120d864e'
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    try:
        # 请求微信接口获取openid
        response = requests.get(url)
        response_data = response.json()
        logger.info(f"微信登录接口返回结果：{response_data}")

        # 检查微信接口返回错误
        if 'errcode' in response_data:
            error_msg = response_data.get('errmsg', '微信接口请求失败')
            logger.error(f"微信接口错误: {error_msg}")
            return jsonify({"error": error_msg, "errcode": response_data['errcode']}), 400

        # 获取openid
        openid = response_data.get('openid')
        if not openid:
            logger.error("微信响应中未找到openid")
            return jsonify({"error": "无法获取用户标识"}), 400

        logger.info(f"获取到用户openid: {openid}")

        # 第一步：根据openid判断用户是否存在
        user = get_user_by_openid(openid)  # 直接调用service层方法

        # 第二步：处理用户存在/不存在的情况
        if user:
            # 更新最后登录时间
            update_user(openid, last_login_at=datetime.utcnow())
            logger.info(f"用户 {openid} 登录成功")
            return jsonify({
                "message": "登录成功",
                "user": user.to_dict(),
                "code": 200
            }), 200
        else:
            # 用户不存在，返回所有用户列表供选择绑定
            all_users = get_all_users()
            logger.info(f"未注册用户，返回{len(all_users)}个用户供选择")
            return jsonify({
                "message": "未注册用户，请选择绑定账号",
                "users": [u.to_dict() for u in all_users]
            }), 200

    except Exception as e:
        logger.exception(f"登录处理异常: {str(e)}")
        return jsonify({"error": "服务器处理请求失败"}), 500


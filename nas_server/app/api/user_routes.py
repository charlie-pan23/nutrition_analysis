# api/user_routes.py
from flask import Blueprint, jsonify, request
# 导入用户服务中的所有功能。
# 蓝图只负责路由和请求/响应处理，具体的业务逻辑和数据库操作都委托给 service 层。
from app.services.user_service import add_user, delete_user, update_user, get_user_by_openid, get_all_users

# 创建一个蓝图实例
# 'user_bp' 是这个蓝图的名称，用于 Flask 内部识别和 URL 构建。
# __name__ 是当前模块的导入名称，Flask 用它来定位资源。
# url_prefix='/users' 意味着所有在这个蓝图下定义的路由都会以 /users 开头。
# 例如，本文件中定义的 '/' 路由，最终将通过主应用访问为 '/users/'。
user_bp = Blueprint('user_bp', __name__, url_prefix='/users')


@user_bp.route('/', methods=['POST'])
def api_add_user():
    """
    API endpoint to add a new user.
    Method: POST
    URL: /users/
    Request Body: JSON object with user details (e.g., {"openid": "abc", "nickname": "test"})
    """
    data = request.json # 获取请求体中的 JSON 数据
    if not data or 'openid' not in data:
        # 如果请求体为空或缺少openid，返回 400 Bad Request
        return jsonify({"error": "缺少openid或请求体为空"}), 400

    # 调用 user_service 中的函数来检查用户是否已存在，避免重复创建
    existing_user = get_user_by_openid(data['openid'])
    if existing_user:
        # 如果用户已存在，返回 200 OK 并告知用户已存在，而不是 409 Conflict，具体取决于业务需求。
        # 这里返回现有用户的信息，方便前端处理。
        return jsonify({"message": f"用户 {data['openid']} 已存在。", "user": existing_user.to_dict()}), 200

    # 调用 user_service 中的函数来添加新用户
    new_user = add_user(**data) # 使用 **data 将字典解包为关键字参数
    if new_user:
        # 添加成功，返回 201 Created 状态码
        return jsonify({"message": "用户添加成功", "user": new_user.to_dict()}), 201
    # 添加失败，返回 500 Internal Server Error
    return jsonify({"error": "用户添加失败"}), 500

@user_bp.route('/<string:openid>', methods=['GET'])
def api_get_user(openid):
    """
    API endpoint to retrieve a single user by openid.
    Method: GET
    URL: /users/<openid>
    """
    # 调用 user_service 中的函数来获取用户
    user = get_user_by_openid(openid)
    if user:
        # 找到用户，返回 200 OK
        return jsonify({"message": "用户获取成功", "user": user.to_dict()}), 200
    # 用户未找到，返回 404 Not Found
    return jsonify({"error": "用户未找到"}), 404

@user_bp.route('/<string:openid>', methods=['PUT'])
def api_update_user(openid):
    """
    API endpoint to update an existing user by openid.
    Method: PUT
    URL: /users/<openid>
    Request Body: JSON object with fields to update (e.g., {"nickname": "new_name"})
    """
    data = request.json
    if not data:
        return jsonify({"error": "请求体为空"}), 400
    # 调用 user_service 中的函数来更新用户
    updated_user = update_user(openid, **data)
    if updated_user:
        # 更新成功，返回 200 OK
        return jsonify({"message": "用户更新成功", "user": updated_user.to_dict()}), 200
    # 更新失败或用户不存在，返回 404 Not Found
    return jsonify({"error": "用户更新失败或用户不存在"}), 404

@user_bp.route('/<string:openid>', methods=['DELETE'])
def api_delete_user(openid):
    """
    API endpoint to delete a user by openid.
    Method: DELETE
    URL: /users/<openid>
    """
    # 调用 user_service 中的函数来删除用户
    if delete_user(openid):
        # 删除成功，返回 200 OK
        return jsonify({"message": f"用户 {openid} 删除成功"}), 200
    # 删除失败或用户不存在，返回 404 Not Found
    return jsonify({"error": "用户删除失败或用户不存在"}), 404

@user_bp.route('/', methods=['GET'])
def api_get_all_users():
    """
    API endpoint to retrieve all users.
    Method: GET
    URL: /users/
    """
    # 调用 user_service 中的函数来获取所有用户
    users = get_all_users()
    # 将用户列表转换为字典列表，便于 JSON 序列化
    return jsonify({"message": "所有用户获取成功", "users": [user.to_dict() for user in users]}), 200


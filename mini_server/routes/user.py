# user_routes.py
from flask import Blueprint, request, jsonify
from mini_server.service.user_service import (
    add_user, delete_user, update_user,
    get_user_by_openid, get_all_users
)

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    user = add_user(**data)
    return jsonify(user.to_dict()), 201 if user else 400

@user_bp.route('/<string:openid>', methods=['DELETE'])
def remove_user(openid):
    success = delete_user(openid)
    return '', 204 if success else 404

@user_bp.route('/<string:openid>', methods=['PUT'])
def modify_user(openid):
    data = request.get_json()
    updated = update_user(openid, **data)
    return jsonify(updated.to_dict()) if updated else ('', 404)

@user_bp.route('/<string:openid>', methods=['GET'])
def get_user(openid):
    user = get_user_by_openid(openid)
    return jsonify(user.to_dict()) if user else ('', 404)

@user_bp.route('', methods=['GET'])
def list_users():
    users = get_all_users()
    return jsonify([user.to_dict() for user in users])
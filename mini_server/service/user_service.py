from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from base import engine

import logging

from models.User import User

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

def add_user(**kwargs):
    """
    向数据库添加一个新用户。
    :param kwargs: 包含用户数据的字典，如 openid, nickname 等。
    :return: User 对象如果成功，否则返回 None。
    """
    try:
        new_user = User(**kwargs) # 使用 kwargs 直接创建 User 实例
        session.add(new_user) # 添加到会话
        session.commit()      # 提交会话，将数据写入数据库
        logger.info(f"用户 {new_user.openid} 添加成功。")
        return new_user
    except SQLAlchemyError as e:
        session.rollback() # 如果发生错误，回滚会话，撤销未提交的更改
        logger.error(f"添加用户失败: {e}", exc_info=True) # 记录详细错误信息
        return None

def delete_user(openid):
    """
    从数据库中删除一个用户。
    :param openid: 用户的唯一标识符。
    :return: True 如果删除成功，False 如果失败或用户不存在。
    """
    try:
        user = session.query(User).filter(User.openid == openid).first()
        if user:
            session.delete(user)  # 从会话中删除用户
            session.commit()      # 提交会话
            logger.info(f"用户 {openid} 删除成功。")
            return True
        logger.warning(f"尝试删除用户 {openid} 失败：用户不存在。")
        return False
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"删除用户 {openid} 失败: {e}", exc_info=True)
        return False

def update_user(openid, **kwargs):
    """
    更新用户信息。
    :param openid: 用户的唯一标识符。
    :param kwargs: 要更新的字段及其新值的字典。
    :return: 更新后的 User 对象如果成功，否则返回 None。
    """
    try:
        user = session.query(User).filter_by(openid=openid).first()
        if user:
            for key, value in kwargs.items():
                # 确保只更新模型中存在的属性，避免意外错误
                if hasattr(user, key):
                    setattr(user, key, value) # 使用 setattr 动态设置属性值
            session.commit()
            logger.info(f"用户 {openid} 更新成功。")
            return user
        logger.warning(f"尝试更新用户 {openid} 失败：用户不存在。")
        return None
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"更新用户 {openid} 失败: {e}", exc_info=True)
        return None

def get_user_by_openid(openid):
    """
    根据 openid 获取单个用户。
    :param openid: 用户的唯一标识符。
    :return: User 对象如果找到，否则返回 None。
    """
    try:
        user = session.query(User).filter(User.openid == openid).first()
        if user:
            logger.info(f"成功获取用户 {openid}。")
            return user
        logger.info(f"用户 {openid} 未找到。")
        return None
    except SQLAlchemyError as e:
        logger.error(f"获取用户 {openid} 失败: {e}", exc_info=True)
        return None

def get_all_users():
    """
    获取所有用户。
    :return: User 对象列表。
    """
    try:
        users = session.query(User).all() # 获取所有用户
        logger.info(f"成功获取所有用户列表，共 {len(users)} 条。")
        return users
    except SQLAlchemyError as e:
        logger.error(f"获取所有用户失败: {e}", exc_info=True)
        return []

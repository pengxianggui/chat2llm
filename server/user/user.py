# 获取当前登录用户
from fastapi import Depends

from server.db.models.user_model import UserModel
from server.user_context.interceptor import get_current_user
from server.utils import BaseResponse


# 获取当前登录用户
def get_user_info(user: UserModel = Depends(get_current_user)):
    return BaseResponse(data=user)

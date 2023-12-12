from typing import Optional

from fastapi import Body, Depends

from server.db.repository import list_histories_form_db
from server.user_context.interceptor import get_current_user
from server.user_context.user_model import User
from server.utils import BaseResponse


def list_histories(
        session_id: str = Body(..., description="会话id"),
        chat_id: str = Body(None, description="聊天记录id"),
        num: int = Body(..., description="获取几轮对话记录"),
        user: User = Depends(get_current_user)):
    # TODO 校验user的合法性
    return BaseResponse(data=list_histories_form_db(session_id=session_id, chat_history_id=chat_id, num=num))

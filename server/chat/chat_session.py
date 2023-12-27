from http.client import HTTPException

from fastapi import Depends, Body

from server.chat.utils import SessionParam
from server.db.models.user_model import UserModel
from server.db.repository import list_sessions, save_session, get_session, delete_session
from server.user_context.interceptor import get_current_user
from server.user_context.user_model import User
from server.utils import BaseResponse


# 我的会话列表
def list_session_from_db(user: User = Depends(get_current_user)):
    return BaseResponse(data=list_sessions(client_id=user.client_id, user_id=user.user_id))


def save_session_to_db(
        session_id: str = Body(..., min_length=32, max_length=32, description="会话id"),
        session_name: str = Body(..., max_length=20, description="会话名", examples=["成语接龙"]),
        mode: str = Body(..., max_length=20, description="模式", examples=["LLM"]),
        param: SessionParam = Body({}, description="会话参数", examples=[{
            "query": "",
            "model_name": "zhipu-api",
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000,
            "prompt_name": "default",
            "history_count": 5,
            "knowledge_base_name": "",
            "top_k": 3,
            "score_threshold": 1,
            "split_result": False
        }]),
        user: UserModel = Depends(get_current_user)):
    return BaseResponse(data=save_session(session_id, user.client_id, user.user_id, mode, session_name, param))


def delete_session_from_db(session_id: str, user: UserModel = Depends(get_current_user)):
    s = get_session(session_id)
    if not s:
        return
    if s.client_id == user.client_id and s.user_id == user.user_id:
        delete_session(session_id)

    raise HTTPException(status_code=403, detail="您无此会话的删除权限!")

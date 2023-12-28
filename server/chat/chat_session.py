from http.client import HTTPException

from fastapi import Depends, Body

from server.chat.utils import SessionParam
from server.db.models.chat_session_model import ChatSessionModel
from server.db.models.user_model import UserModel
from server.db.repository import list_sessions, save_session, get_session, delete_session, get_sessions, \
    delete_sessions, delete_history_by_session, delete_history_by_sessions
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


# 批量删除会话
def delete_sessions_from_db(session_ids: list = Body(..., description="要删除的会话id数组"),
                           user: UserModel = Depends(get_current_user)):
    sessions = get_sessions(session_ids)
    if len(sessions) == 0:
        return BaseResponse(data=True)

    session_ids_belong_user = [s.id for s in sessions if s.client_id == user.client_id and s.user_id == user.user_id]
    delete_sessions(session_ids_belong_user)
    delete_history_by_sessions(session_ids_belong_user)
    return BaseResponse(data=True)


# 删除会话
def delete_session_from_db(session_id: str = Body(..., min_length=32, max_length=32, description="要删除的会话id"),
                           user: UserModel = Depends(get_current_user)):
    session: ChatSessionModel = get_session(session_id)
    if session is None:
        return BaseResponse(data=True)
    if session.user_id == user.user_id and session.client_id == user.client_id:
        delete_session(session_id)
        delete_history_by_session(session_id)
        return BaseResponse(data=True)
    raise HTTPException(status_code=403, detail=f"无权操作!")



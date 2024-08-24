from sqlalchemy import desc, and_

from server.db.session import with_session
from server.db.models.chat_history_model import ChatHistoryModel
import re
import uuid
from typing import Dict, List


def _convert_query(query: str) -> str:
    p = re.sub(r"\s+", "%", query)
    return f"%{p}%"


@with_session
def add_chat_history_to_db(session, session_id, chat_type, query, response="", chat_history_id=None,
                           metadata: Dict = {}):
    """
    新增聊天记录
    """
    if not chat_history_id:
        chat_history_id = uuid.uuid4().hex
    ch = ChatHistoryModel(id=chat_history_id, session_id=session_id, chat_type=chat_type, query=query,
                          response=response, metadata=metadata)
    session.add(ch)
    session.commit()
    return ch.id


@with_session
def update_chat_history(session, chat_history_id, response: str = None, docs=[], metadata: Dict = None):
    """
    更新已有的聊天记录
    """
    ch = get_chat_history_by_id(chat_history_id)
    if ch is not None:
        if response is not None:
            ch.response = response
        if docs is not None:
            ch.docs = docs
        if isinstance(metadata, dict):
            ch.meta_data = metadata
        session.add(ch)
        return ch.id

@with_session
def exist_chat_history_id(session, chat_history_id: str):
    ch = session.query(ChatHistoryModel).filter_by(id=chat_history_id).first()
    return ch is not None

@with_session
def feedback_chat_history_to_db(session, chat_history_id, feedback_score, feedback_reason):
    """
    反馈聊天记录
    """
    ch = session.query(ChatHistoryModel).filter_by(id=chat_history_id).first()
    if ch:
        ch.feedback_score = feedback_score
        ch.feedback_reason = feedback_reason
        return ch.id


@with_session
def get_chat_history_by_id(session, chat_history_id) -> ChatHistoryModel:
    """
    查询聊天记录
    """
    ch = session.query(ChatHistoryModel).filter_by(id=chat_history_id).first()
    if ch is not None:
        session.expunge(ch)  # 会话关闭后保持ch值有效
    return ch


@with_session
def filter_chat_history(session, query=None, response=None, score=None, reason=None) -> List[ChatHistoryModel]:
    ch = session.query(ChatHistoryModel)
    if query is not None:
        ch = ch.filter(ChatHistoryModel.query.ilike(_convert_query(query)))
    if response is not None:
        ch = ch.filter(ChatHistoryModel.response.ilike(_convert_query(response)))
    if score is not None:
        ch = ch.filter_by(feedback_score=score)
    if reason is not None:
        ch = ch.filter(ChatHistoryModel.feedback_reason.ilike(_convert_query(reason)))

    return ch


# 获取指定记录的前num条记录。倒序
@with_session
def list_histories_form_db(session, session_id, chat_history_id, num):
    data = []
    histories = []
    if chat_history_id is None:
        # 获取session_id最新的num条记录
        histories = session.query(ChatHistoryModel).filter_by(session_id=session_id).order_by(
            desc(ChatHistoryModel.create_time)).limit(num).all()
    else:
        # 获取指定chat_history_id前最新的num条记录
        chat: ChatHistoryModel = get_chat_history_by_id(chat_history_id)
        if chat is not None:
            histories = (session.query(ChatHistoryModel)
                         .filter(and_(ChatHistoryModel.session_id == session_id, ChatHistoryModel.create_time < str(chat.create_time)))  # 日期转为str防止毫秒的000影响结果
                         .order_by(desc(ChatHistoryModel.create_time)).limit(num).all())

    if len(histories) > 0:
        for h in histories:
            data.append({
                "id": h.id,
                "query": h.query,
                "response": h.response,
                "docs": h.docs,
                "create_time": h.create_time
            })

    return data


# 删除单个会话关联的对话记录
@with_session
def delete_history_by_session(session, session_id):
    session.query(ChatHistoryModel).filter_by(session_id=session_id).delete()


# 删除多个会话关联的对话记录
def delete_history_by_sessions(session, session_ids):
    session.query(ChatHistoryModel).fillter(ChatHistoryModel.session_id.in_(session_ids)).delete()

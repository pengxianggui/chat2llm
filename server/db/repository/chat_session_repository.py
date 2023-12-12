import json

from server.db.session import with_session
from server.db.models.chat_session_model import ChatSessionModel


@with_session
def save_session(session, session_id, client_id, user_id, mode, session_name, param):
    s = session.query(ChatSessionModel).filter_by(id=session_id).first()
    if not s:
        s = ChatSessionModel(id=session_id, client_id=client_id, user_id=user_id, mode=mode, session_name=session_name,
                             param=json.dumps(param.__dict__))
        session.add(s)
    else:
        if not mode:
            s.mode = mode
        if not session_name:
            s.session_name = session_name
        if not param:
            s.param = json.dumps(param.__dict__)
    return True


@with_session
def list_sessions(session, client_id, user_id):
    data = []
    sessions = session.query(ChatSessionModel).filter_by(client_id=client_id, user_id=user_id).all()
    if len(sessions) > 0:
        for s in sessions:
            data.append({
                "session_id": s.id,
                "session_name": s.session_name,
                "mode": s.mode,
                "param": s.param,
                "create_time": s.create_time
            })
    return data


@with_session
def delete_session(session, session_id):
    s = session.query(ChatSessionModel).filter_by(id=session_id).first()
    if s:
        session.delete(s)
    return True


@with_session
def get_session(session, session_id):
    s = session.query(ChatSessionModel).filter_by(id=session_id).first()
    if not s:
        return None
    return ChatSessionModel(id=s.id, client_id=s.client_id, user_id=s.user_id, mode=s.mode,
                            session_name=s.session_name, param=s.param, create_time=s.create_time)

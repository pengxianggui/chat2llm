from sqlalchemy import Column, String, DateTime, JSON, func

from server.db.base import Base


class ChatSessionModel(Base):
    """
    聊天记录模型
    """
    __tablename__ = 'chat_session'
    # 由前端生成的uuid
    id = Column(String(32), primary_key=True, comment='聊天记录ID')
    client_id = Column(String(32), comment='客户端id')
    user_id = Column(String(64), comment='用户id')
    mode = Column(String(20), comment='模式(LLM,Knowledge,SearchEngine,Agent)')
    session_name = Column(String(20), comment='会话名')
    param = Column(JSON, default={}, comment='会话参数')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<ChatSession(id='{self.id}', client_id='{self.client_id}', user_id='{self.user_id}', mode='{self.mode}',session_name='{self.session_name}',param='{self.param}', create_time='{self.create_time}')>"

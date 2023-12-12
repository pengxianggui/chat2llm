from sqlalchemy import Column, String, DateTime, func, Boolean

from server.db.base import Base


class UserModel(Base):
    """
    聊天记录模型
    """
    __tablename__ = 'user'
    client_id = Column(String(32), primary_key=True, comment='客户端id')
    user_id = Column(String(64), primary_key=True, comment='用户id')
    username = Column(String(50), comment='用户名')
    enable = Column(Boolean, default=True, comment='启用')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<User(client_id='{self.client_id}', user_id='{self.user_id}', username='{self.username}',enable='{self.enable}', create_time='{self.create_time}')>"

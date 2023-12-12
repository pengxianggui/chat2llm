from sqlalchemy import Column, String, DateTime, func, Boolean

from server.db.base import Base


class ClientModel(Base):
    """
    聊天记录模型
    """
    __tablename__ = 'client'
    id = Column(String(32), primary_key=True, comment='客户端id')
    client_key = Column(String(2048), comment='公钥')
    client_secret = Column(String(2048), comment='密钥')
    description = Column(String(100), comment='描述')
    enable = Column(Boolean, default=True, comment='启用')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<Client(id='{self.id}', client_key='{self.client_key}', client_secret='{self.client_secret}', description='{self.description}',enable='{self.enable}', create_time='{self.create_time}')>"

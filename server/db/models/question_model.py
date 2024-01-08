from sqlalchemy import Column, String, DateTime, func, Boolean, Integer

from server.db.base import Base


class QuestionModel(Base):
    """
    聊天记录模型
    """
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='问题id')
    query = Column(String(200), comment='预设问题内容')
    kb_name = Column(String(50), comment='知识库名(为空则使用llm对话)')
    answer = Column(String(2048), comment='预设答案(此值内容可以取自管理员维护、或者取自最高点赞的AI回答)')
    tap_count = Column(Integer, default=0, comment='点击次数')
    enable = Column(Boolean, default=True, comment='启用(false则不会被推荐)')
    create_time = Column(DateTime, default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<Question(id='{self.id}', query='{self.query}', kb_name='{self.kb_name}', answer='{self.answer}',tap_count='{self.tap_count}',enable='{self.enable}', create_time='{self.create_time}')>"

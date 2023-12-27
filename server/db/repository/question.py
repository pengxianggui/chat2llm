from sqlalchemy import desc
from sqlalchemy.sql.functions import random

from server.db.models.question_model import QuestionModel
from server.db.session import with_session


# 随机从预设问题集中获取指定数量的问题
@with_session
def list_random_questions(session, num):
    data = []
    questions = session.query(QuestionModel).order_by(random()).limit(num).all()
    for q in questions:
        session.expunge(q)
        data.append(q)
    return data

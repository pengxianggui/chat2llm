from sqlalchemy import desc, or_
from sqlalchemy.sql.functions import random

from server.db.models.question_model import QuestionModel
from server.db.session import with_session


# 随机从预设问题集中获取指定数量的问题。kb_name不传则不限定范围;传了空串则限定非知识库;传了非空串则限定知识库
@with_session
def list_random_questions(session, kb_name, num):
    data = []
    query = session.query(QuestionModel)
    if kb_name is None:
        questions = query.order_by(random()).limit(num).all()
    elif kb_name == "":
        questions = query.filter_by(kb_name=None).order_by(random()).limit(num).all()
    else:
        questions = query.filter_by(kb_name=kb_name).order_by(random()).limit(num).all()
    for q in questions:
        session.expunge(q)
        data.append(q)
    return data

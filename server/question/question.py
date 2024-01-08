from fastapi import Query, Body

from server.db.repository.question import list_random_questions, save_question
from server.utils import BaseResponse


def list_recommend_question(kb_name: str = Query(None, description="知识库名(不传则不限定范围;传了空串则限定非知识库;传了非空串则限定知识库)"),
                            num: int = Query(..., description="会话id")):
    # todo 这里应该根据用户画像(例如经常咨询的问题、所属部门等)来推荐不同的问题。目前无用户画像，就随机给表中的一些
    return BaseResponse(data=list_random_questions(kb_name=kb_name, num=num))


def save_recommend_question(question_id: int = Body(None, description="不为空则视为更新"),
                            query: str = Body(..., description="问题内容"),
                            kb_name: str = Body(None, description="所属知识库, 为空则LLM对话模式")):
    return BaseResponse(data=save_question(id=question_id, query=query, kb_name=kb_name))

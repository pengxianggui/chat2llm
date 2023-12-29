from fastapi import Query

from server.db.repository.question import list_random_questions
from server.utils import BaseResponse


def list_recommend_question(kb_name: str = Query(None, description="知识库名(不传则不限定范围;传了空串则限定非知识库;传了非空串则限定知识库)"),
                            num: int = Query(..., description="会话id")):
    # todo 这里应该根据用户画像(例如经常咨询的问题、所属部门等)来推荐不同的问题。目前无用户画像，就随机给表中的一些
    return BaseResponse(data=list_random_questions(kb_name=kb_name, num=num))

from fastapi import FastAPI

from server.chat.chat_session import list_session_from_db, save_session_to_db, delete_session_from_db
from server.chat.history import list_histories
from server.knowledge_base.kb_api import list_kbs_v2
from server.knowledge_base.kb_doc_api import update_zh_name
from server.question.question import list_recommend_question
from server.user_context.client import redirect_h5_demo
from server.utils import BaseResponse


# 挂载自定义的知识库相关的路由接口
def mount_custom_knowledge_routes(app: FastAPI):
    app.get('/knowledge_base/list_knowledge_bases_v2',
            tags=["Knowledge Base Management"],
            response_model=BaseResponse,
            summary="获取知识库列表")(list_kbs_v2)
    app.post("/knowledge_base/update_zh_name",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新知识库中文名"
             )(update_zh_name)


# 挂载自定义的其它路由接口
def mount_custom_other_routes(app: FastAPI):
    app.get("/h5-demo",
            tags=["Other"],
            summary="重定向到h5 demo页面。不携带token而直接访问h5页面将返回401, 但是通过此接口将重定向的h5页面可正常使用。注意: 仅限演示使用"
            )(redirect_h5_demo)


# 挂载自定义会话相关的路由接口
def mount_custom_session_routes(app: FastAPI):
    app.get("/session/list",
            tags=["Session Management"],
            summary="我的会话列表")(list_session_from_db)

    app.post("/session/save",
             tags=["Session Management"],
             summary="保存会话")(save_session_to_db)

    app.post("/session/delete",
             tags=["Session Management"],
             summary="删除会话")(delete_session_from_db)


# 挂载自定义聊天历史相关的路由接口
def mount_custom_chat_history_routes(app: FastAPI):
    app.post('/history/latest',
             tags=["History Management"],
             summary="获取指定会话的指定历史记录")(list_histories)


# 挂载推荐内容
def mount_custom_recommend_routes(app: FastAPI):
    app.get('/recommend/question',
            tags=["Recommend Management"],
            summary="获取推荐的问题")(list_recommend_question)

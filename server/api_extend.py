from fastapi import FastAPI

from server.chat.chat_session import list_session_from_db, save_session_to_db, delete_session_from_db
from server.chat.history import list_histories
from server.knowledge_base.kb_api import list_kbs_v2
from server.knowledge_base.kb_doc_api import update_zh_name
from server.question.question import list_recommend_question, save_recommend_question
from server.user.user import get_user_info
from server.user_context.sso import ent_wechat_sso, sso_handler
from server.utils import BaseResponse


# 挂载自定义的路由接口
def mount_custom_routes(app: FastAPI):
    mount_custom_user_routes(app)
    mount_custom_knowledge_routes(app)
    mount_custom_sso_routes(app)
    mount_custom_session_routes(app)
    mount_custom_chat_history_routes(app)
    mount_custom_recommend_routes(app)


# 挂载用户相关接口
def mount_custom_user_routes(app: FastAPI):
    app.get('/user/info',
            tags=["User Management"],
            response_model=BaseResponse,
            summary="获取用户信息")(get_user_info)


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

    app.post('/recommend/question',
             tags=["Recommend Management"],
             summary="添加推荐的问题")(save_recommend_question)


# 挂载自定义的其它路由接口
def mount_custom_sso_routes(app: FastAPI):
    app.get("/sso",
            tags=["SSO"],
            summary="单点登录接口. h5访问时单点登录统一入口"
            )(sso_handler)

    app.get("/ent-wechat-sso",
            tags=["Other"],
            summary="企微单点登录回调地址, 提供给企微使用的"
            )(ent_wechat_sso)

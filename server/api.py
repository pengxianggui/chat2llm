import os
import sys

import nltk

from server.chat.chat_session import list_session_from_db, save_session_to_db, delete_session_from_db
from server.chat.history import list_histories
from server.user_context.client import redirect_h5_demo
from server.user_context.interceptor import TokenMiddleware

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from configs import VERSION
from configs.model_config import NLTK_DATA_PATH
from configs.server_config import OPEN_CROSS_DOMAIN
import argparse
import uvicorn
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from server.chat.chat import chat
from server.chat.openai_chat import openai_chat
from server.chat.search_engine_chat import search_engine_chat
from server.chat.completion import completion
from server.chat.feedback import chat_feedback
from server.embeddings_api import embed_texts_endpoint
from server.llm_api import (list_running_models, list_config_models,
                            change_llm_model, stop_llm_model,
                            get_model_config, list_search_engines)
from server.utils import (BaseResponse, ListResponse, FastAPI, MakeFastAPIOffline,
                          get_server_configs, get_prompt_template)
from typing import List, Literal

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path


async def document():
    return RedirectResponse(url="/docs")


def create_app(run_mode: str = None):
    app = FastAPI(
        title="Chat2LLM API Server",
        version=VERSION
    )
    MakeFastAPIOffline(app)
    # Add CORS middleware to allow all origins
    # 在config.py中设置OPEN_DOMAIN=True，允许跨域
    # set OPEN_DOMAIN=True in config.py to allow cross-domain
    if OPEN_CROSS_DOMAIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    mount_app_routes(app, run_mode=run_mode)
    app.add_middleware(TokenMiddleware)  # token认证

    return app


def mount_app_routes(app: FastAPI, run_mode: str = None):
    app.get("/",
            response_model=BaseResponse,
            summary="swagger 文档")(document)

    # Tag: Chat
    app.post("/chat/fastchat",
             tags=["Chat"],
             summary="与llm模型对话(直接与fastchat api对话)",
             )(openai_chat)

    app.post("/chat/chat",
             tags=["Chat"],
             summary="与llm模型对话(通过LLMChain)",
             )(chat)

    app.post("/chat/search_engine_chat",
             tags=["Chat"],
             summary="与搜索引擎对话",
             )(search_engine_chat)

    app.post("/chat/feedback",
             tags=["Chat"],
             summary="返回llm模型对话评分",
             )(chat_feedback)

    # 知识库相关接口
    mount_knowledge_routes(app)

    # LLM模型相关接口
    app.post("/llm_model/list_running_models",
             tags=["LLM Model Management"],
             summary="列出当前已加载的模型",
             )(list_running_models)

    app.post("/llm_model/list_config_models",
             tags=["LLM Model Management"],
             summary="列出configs已配置的模型",
             )(list_config_models)

    app.post("/llm_model/get_model_config",
             tags=["LLM Model Management"],
             summary="获取模型配置（合并后）",
             )(get_model_config)

    app.post("/llm_model/stop",
             tags=["LLM Model Management"],
             summary="停止指定的LLM模型（Model Worker)",
             )(stop_llm_model)

    app.post("/llm_model/change",
             tags=["LLM Model Management"],
             summary="切换指定的LLM模型（Model Worker)",
             )(change_llm_model)

    # 会话相关接口
    app.get("/session/list",
             tags=["Session Management"],
             summary="我的会话列表")(list_session_from_db)

    app.post("/session/save",
             tags=["Session Management"],
             summary="保存会话")(save_session_to_db)

    app.post("/session/delete",
             tags=["Session Management"],
             summary="删除会话")(delete_session_from_db)

    # 聊天历史相关接口
    app.post('/history/latest',
            tags=["History Management"],
            summary="获取指定会话的指定历史记录")(list_histories)

    # 服务器相关接口
    app.post("/server/configs",
             tags=["Server State"],
             summary="获取服务器原始配置信息",
             )(get_server_configs)

    app.post("/server/list_search_engines",
             tags=["Server State"],
             summary="获取服务器支持的搜索引擎",
             )(list_search_engines)

    @app.post("/server/get_prompt_template",
              tags=["Server State"],
              summary="获取服务区配置的 prompt 模板")
    def get_server_prompt_template(
            type: Literal["llm_chat", "knowledge_base_chat", "search_engine_chat", "agent_chat"] = Body("llm_chat",
                                                                                                        description="模板类型，可选值：llm_chat，knowledge_base_chat，search_engine_chat，agent_chat"),
            name: str = Body("default", description="模板名称"),
    ) -> str:
        return get_prompt_template(type=type, name=name)

    # 其它接口
    app.post("/other/completion",
             tags=["Other"],
             summary="要求llm模型补全(通过LLMChain)",
             )(completion)

    app.post("/other/embed_texts",
             tags=["Other"],
             summary="将文本向量化，支持本地模型和在线模型",
             )(embed_texts_endpoint)

    app.get("/h5-demo",
            tags=["Other"],
            summary="重定向到h5 demo页面。不携带token而直接访问h5页面将返回401, 但是通过此接口将重定向的h5页面可正常使用。注意: 仅限演示使用"
            )(redirect_h5_demo)


def mount_knowledge_routes(app: FastAPI):
    from server.chat.knowledge_base_chat import knowledge_base_chat
    from server.chat.agent_chat import agent_chat
    from server.knowledge_base.kb_api import list_kbs, list_kbs_v2, create_kb, delete_kb
    from server.knowledge_base.kb_doc_api import (list_files, upload_docs, delete_docs,
                                                  update_docs, download_doc, recreate_vector_store,
                                                  search_docs, DocumentWithScore, update_zh_name, update_info)

    app.post("/chat/knowledge_base_chat",
             tags=["Chat"],
             summary="与知识库对话")(knowledge_base_chat)

    app.post("/chat/agent_chat",
             tags=["Chat"],
             summary="与agent对话")(agent_chat)

    # Tag: Knowledge Base Management
    app.get("/knowledge_base/list_knowledge_bases",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库名称列表")(list_kbs)

    app.get('/knowledge_base/list_knowledge_bases_v2',
            tags=["Knowledge Base Management"],
            response_model=BaseResponse,
            summary="获取知识库列表")(list_kbs_v2)

    app.post("/knowledge_base/create_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="创建知识库"
             )(create_kb)

    app.post("/knowledge_base/delete_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库"
             )(delete_kb)

    app.get("/knowledge_base/list_files",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库内的文件列表"
            )(list_files)

    app.post("/knowledge_base/search_docs",
             tags=["Knowledge Base Management"],
             response_model=List[DocumentWithScore],
             summary="搜索知识库"
             )(search_docs)

    app.post("/knowledge_base/upload_docs",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="上传文件到知识库，并/或进行向量化"
             )(upload_docs)

    app.post("/knowledge_base/delete_docs",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库内指定文件"
             )(delete_docs)

    app.post("/knowledge_base/update_zh_name",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新知识库中文名"
             )(update_zh_name)

    app.post("/knowledge_base/update_info",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新知识库介绍"
             )(update_info)

    app.post("/knowledge_base/update_docs",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新现有文件到知识库"
             )(update_docs)

    app.get("/knowledge_base/download_doc",
            tags=["Knowledge Base Management"],
            summary="下载对应的知识文件")(download_doc)

    app.post("/knowledge_base/recreate_vector_store",
             tags=["Knowledge Base Management"],
             summary="根据content中文档重建向量库，流式输出处理进度。"
             )(recreate_vector_store)


def run_api(host, port, **kwargs):
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app,
                    host=host,
                    port=port,
                    ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"),
                    )
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='langchain-ChatGLM',
                                     description='About langchain-ChatGLM, local knowledge based ChatGLM with langchain'
                                                 ' ｜ 基于本地知识库的 ChatGLM 问答')
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7861)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)

    app = create_app()
    mount_knowledge_routes(app)

    run_api(host=args.host,
            port=args.port,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            )

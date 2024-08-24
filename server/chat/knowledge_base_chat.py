import traceback

from fastapi import Body, Request
from fastapi.responses import StreamingResponse
from configs import (VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, TEMPERATURE, SAVE_CHAT_HISTORY, ENABLE_LLM_MODEL,
                     ENABLE_AZS, HISTORY_LEN)
from server.third.azs_http import fetch_with_streaming
from server.db.repository import add_chat_history_to_db, update_chat_history, exist_chat_history_id
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable, List, Optional
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from server.chat.utils import History
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.knowledge_base.utils import get_doc_path
import json
from pathlib import Path
from urllib.parse import urlencode
from server.knowledge_base.kb_doc_api import search_docs


async def knowledge_base_chat(session_id: str = Body(None, min_length=32, max_length=32, description="会话id"),
                              chat_history_id: str = Body(None,
                                                          description="若有值表示是基于此对话记录重新生成。此时提问不入库，回答做更新"),
                              query: str = Body(..., description="用户输入", examples=["你好"]),
                              knowledge_base_id: str = Body(None, description="知识库id(爱助手模式使用)",
                                                            examples=["samples"]),
                              knowledge_base_name: str = Body(None, description="知识库名(缺省模式使用)",
                                                              examples=["samples"]),
                              top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                              score_threshold: float = Body(SCORE_THRESHOLD,
                                                            description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
                                                            ge=0, le=2),
                              history: List[History] = Body([],
                                                            description="历史对话",
                                                            examples=[[
                                                                {"role": "user",
                                                                 "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                                {"role": "assistant",
                                                                 "content": "虎头虎脑"}]]
                                                            ),
                              stream: bool = Body(False, description="流式输出"),
                              model_name: str = Body(ENABLE_LLM_MODEL, description="LLM 模型名称。"),
                              temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                              max_tokens: Optional[int] = Body(None,
                                                               description="限制LLM生成Token数量，默认None代表模型最大值"),
                              prompt_name: str = Body("default",
                                                      description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                              request: Request = None,
                              ):
    history = [History.from_data(h) for h in history]

    # longchain代理的LLM
    async def self_knowledge_base_chat_iterator(knowledge_base_name: str,
                                                query: str,
                                                chat_history_id: str,
                                                top_k: int,
                                                history: Optional[List[History]],
                                                model_name: str = ENABLE_LLM_MODEL,
                                                prompt_name: str = prompt_name,
                                                ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )
        docs = search_docs(query, knowledge_base_name, top_k, score_threshold)
        context = "\n".join([doc.page_content for doc in docs])
        if len(docs) == 0:  ## 如果没有找到相关文档，使用Empty模板
            prompt_template = get_prompt_template("knowledge_base_chat", "Empty")
        else:
            prompt_template = get_prompt_template("knowledge_base_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model)

        answer = ""
        source_documents = []
        try:
            first_answer = chat_history_id is None  # 首次回答
            if first_answer:  # 首次回答(不是重新回答) 则持久化对话记录
                chat_history_id = add_chat_history_to_db(session_id=session_id, chat_type="knowledge_base_chat",
                                                         query=query)

            # Begin a task that runs in the background.
            task = asyncio.create_task(wrap_done(
                chain.acall({"context": context, "question": query}),
                callback.done),
            )

            doc_path = get_doc_path(knowledge_base_name)
            for inum, doc in enumerate(docs):
                filename = Path(doc.metadata["source"]).resolve().relative_to(doc_path)
                parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name": filename})
                base_url = request.base_url
                url = f"{base_url}knowledge_base/download_doc?" + parameters
                text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
                source_documents.append(text)

            if len(source_documents) == 0:  # 没有找到相关文档
                source_documents.append(
                    f"""<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>""")

            if stream:
                async for token in callback.aiter():
                    answer += token
                    # Use server-sent-events to stream the response
                    yield json.dumps({"answer": token}, ensure_ascii=False)
                yield json.dumps({"docs": source_documents}, ensure_ascii=False)
            else:
                async for token in callback.aiter():
                    answer += token
                yield json.dumps({"answer": answer,
                                  "docs": source_documents},
                                 ensure_ascii=False)
        except Exception:
            answer = '抱歉, 请换个问法，我可能没听清.'
            yield json.dumps({"text": answer, "chat_history_id": chat_history_id}, ensure_ascii=False)
        finally:
            if SAVE_CHAT_HISTORY and len(chat_history_id) > 0:
                update_chat_history(chat_history_id, response=answer, docs=source_documents)

        await task

    # 爱助手问答
    async def azs_knowledge_base_chat_iterator(knowledge_base_id: str,
                                               query: str,
                                               chat_history_id: str,
                                               top_k: int
                                               ) -> AsyncIterable[str]:
        queue = asyncio.Queue()
        answer = ""
        try:
            first_answer = not exist_chat_history_id(chat_history_id)  # 不存在这个chat_history_id，则为首次回答
            if first_answer:  # 首次回答(不是重新回答) 则持久化对话记录
                chat_history_id = add_chat_history_to_db(session_id=session_id, chat_type="llm_chat", query=query,
                                                         response=answer, chat_history_id=chat_history_id)
            params = {
                "knowledgeBaseId": knowledge_base_id,
                "stream": True,
                "temperature": TEMPERATURE,
                "top_p": 0.95,
                "max_tokens": 2048,
                "apiThirdSessionId": session_id,
                "contextRecordCount": HISTORY_LEN,
                "presence_penalty": 0,
                "frequency_penalty": 0,
                "messages": [{
                    "content": query,
                    "role": "user"
                }]
            }
            asyncio.create_task(fetch_with_streaming('/v2/kb-chat', params, chat_history_id, queue))
            while True:
                chunk = await queue.get()
                if chunk is None:  # 结束信号
                    break
                answer += json.loads(chunk).get('text', '')
                yield json.dumps({
                    "answer": json.loads(chunk).get('text'),
                    "chat_history_id": chat_history_id
                })

        except Exception:
            traceback.print_exc()  # 打印堆栈信息
            answer = '抱歉, 请换个问法，我可能没听清.'
            yield json.dumps({"answer": answer, "chat_history_id": chat_history_id}, ensure_ascii=False)
        finally:
            if SAVE_CHAT_HISTORY and len(chat_history_id) > 0:
                update_chat_history(chat_history_id, response=answer)

    # 启用爱助手
    if ENABLE_AZS:
        return StreamingResponse(azs_knowledge_base_chat_iterator(knowledge_base_id=knowledge_base_id,
                                                                  query=query,
                                                                  chat_history_id=chat_history_id,
                                                                  top_k=top_k),
                                 media_type="text/event-stream")
    else:  # 自带
        kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
        if kb is None:
            return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")
        return StreamingResponse(self_knowledge_base_chat_iterator(knowledge_base_name=knowledge_base_name,
                                                                   query=query,
                                                                   chat_history_id=chat_history_id,
                                                                   top_k=top_k,
                                                                   history=history,
                                                                   model_name=model_name,
                                                                   prompt_name=prompt_name),
                                 media_type="text/event-stream")

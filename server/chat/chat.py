import asyncio
import json
import traceback
import uuid
from typing import AsyncIterable
from typing import List, Optional

from fastapi import Body
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate

from configs import TEMPERATURE, SAVE_CHAT_HISTORY, ENABLE_LLM_MODEL, HISTORY_LEN, ENABLE_AZS
from server.third.azs_http import fetch_with_streaming
from server.chat.utils import History
from server.db.repository import add_chat_history_to_db, update_chat_history, exist_chat_history_id
from server.utils import get_prompt_template
from server.utils import wrap_done, get_ChatOpenAI


async def chat(session_id: str = Body(None, min_length=32, max_length=32, description="会话id"),
               chat_history_id: str = Body(None,
                                           description="若有值表示是基于此对话记录重新生成。此时提问不入库，回答做更新"),
               query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               history: List[History] = Body([],
                                             description="历史对话",
                                             examples=[[
                                                 {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                 {"role": "assistant", "content": "虎头虎脑"}]]
                                             ),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(ENABLE_LLM_MODEL, description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
               max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               ):
    history = [History.from_data(h) for h in history]

    # longchain代理的LLM
    async def self_chat_iterator(query: str,
                                 chat_history_id: str,
                                 history: List[History] = [],
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

        prompt_template = get_prompt_template("llm_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
        chain = LLMChain(prompt=chat_prompt, llm=model)

        answer = ""
        try:
            first_answer = not exist_chat_history_id(chat_history_id)  # 不存在这个chat_history_id，则为首次回答
            if first_answer:  # 首次回答(不是重新回答) 则持久化对话记录
                chat_history_id = add_chat_history_to_db(session_id=session_id, chat_type="llm_chat", query=query,
                                                         response=answer, chat_history_id=chat_history_id)

            # Begin a task that runs in the background.
            task = asyncio.create_task(wrap_done(
                chain.acall({"input": query}),
                callback.done),
            )

            if stream:
                async for token in callback.aiter():
                    answer += token
                    # Use server-sent-events to stream the response
                    yield json.dumps(
                        {"text": token, "chat_history_id": chat_history_id},
                        ensure_ascii=False)
            else:
                async for token in callback.aiter():
                    answer += token
                yield json.dumps(
                    {"text": answer, "chat_history_id": chat_history_id},
                    ensure_ascii=False)

        except Exception:
            answer = '抱歉, 请换个问法，我可能没听清.'
            yield json.dumps({"text": answer, "chat_history_id": chat_history_id}, ensure_ascii=False)
        finally:
            if SAVE_CHAT_HISTORY and len(chat_history_id) > 0:
                update_chat_history(chat_history_id, response=answer)

        await task

    # 爱助手提供的
    async def azs_chat_iterator(query: str,
                                chat_history_id: str,
                                history: List[History] = [],
                                ) -> AsyncIterable[str]:
        queue = asyncio.Queue()
        answer = ""
        try:
            first_answer = not exist_chat_history_id(chat_history_id)  # 不存在这个chat_history_id，则为首次回答
            if first_answer:  # 首次回答(不是重新回答) 则持久化对话记录
                chat_history_id = add_chat_history_to_db(session_id=session_id, chat_type="llm_chat", query=query,
                                                         response=answer, chat_history_id=chat_history_id)
            params = {
                "model": "gpt-4o",
                "stream": True,
                "temperature": TEMPERATURE,
                "top_p": 0.95,
                "apiThirdSessionId": session_id,
                "contextRecordCount": HISTORY_LEN,
                "messages": [{
                    "content": query,
                    "role": "user"
                }]
            }
            asyncio.create_task(fetch_with_streaming('/v2/chat', params, chat_history_id, queue))
            while True:
                chunk = await queue.get()
                if chunk is None:  # 结束信号
                    break
                answer += json.loads(chunk).get('text', '')
                yield chunk

        except Exception:
            traceback.print_exc()  # 打印堆栈信息
            answer = '抱歉, 请换个问法，我可能没听清.'
            yield json.dumps({"text": answer, "chat_history_id": chat_history_id}, ensure_ascii=False)
        finally:
            if SAVE_CHAT_HISTORY and len(chat_history_id) > 0:
                update_chat_history(chat_history_id, response=answer)

    if chat_history_id is None:
        chat_history_id = uuid.uuid4().hex
    # 根据参数配置决定走哪个逻辑
    if ENABLE_AZS:
        return StreamingResponse(azs_chat_iterator(query=query,
                                                   chat_history_id=chat_history_id,
                                                   history=history),
                                 media_type="text/event-stream")
    else:
        return StreamingResponse(self_chat_iterator(query=query,
                                                    chat_history_id=chat_history_id,
                                                    history=history,
                                                    model_name=model_name,
                                                    prompt_name=prompt_name),
                                 media_type="text/event-stream")

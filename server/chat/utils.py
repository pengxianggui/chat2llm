import json
from json import JSONEncoder

from pydantic import BaseModel, Field
from langchain.prompts.chat import ChatMessagePromptTemplate
from configs import logger, log_verbose
from typing import List, Tuple, Dict, Union, Optional


class History(BaseModel):
    """
    对话历史
    可从dict生成，如
    h = History(**{"role":"user","content":"你好"})
    也可转换为tuple，如
    h.to_msy_tuple = ("human", "你好")
    """
    role: str = Field(...)
    content: str = Field(...)

    def to_msg_tuple(self):
        return "ai" if self.role=="assistant" else "human", self.content

    def to_msg_template(self, is_raw=True) -> ChatMessagePromptTemplate:
        role_maps = {
            "ai": "assistant",
            "human": "user",
        }
        role = role_maps.get(self.role, self.role)
        if is_raw: # 当前默认历史消息都是没有input_variable的文本。
            content = "{% raw %}" + self.content + "{% endraw %}"
        else:
            content = self.content

        return ChatMessagePromptTemplate.from_template(
            content,
            "jinja2",
            role=role,
        )

    @classmethod
    def from_data(cls, h: Union[List, Tuple, Dict]) -> "History":
        if isinstance(h, (list,tuple)) and len(h) >= 2:
            h = cls(role=h[0], content=h[1])
        elif isinstance(h, dict):
            h = cls(**h)

        return h


class SessionParam(BaseModel):
    model_name: str = Field(default="zhipu-api")
    query: Optional[str] = Field(default="")
    stream: Optional[bool] = Field(default=True)
    temperature: Optional[float] = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=2000)
    prompt_name: Optional[str] = Field(default="default")
    history_count: Optional[int] = Field(default=5)
    knowledge_base_name: Optional[str] = Field(default="")
    top_k: Optional[int] = Field(default=3)
    score_threshold: Optional[int] = Field(default=1)
    split_result: Optional[bool] = Field(default=False)
#
#     def __iter__(self):
#         yield from {
#             'query': self.query,
#             'model_name': self.model_name,
#             'stream': self.model_name,
#             'temperature': self.temperature,
#             'max_tokens': self.max_tokens,
#             'prompt_name': self.prompt_name,
#             'history_count': self.history_count,
#             'knowledge_base_name': self.knowledge_base_name,
#             'top_k': self.top_k,
#             'score_threshold': self.score_threshold,
#             'split_result': self.split_result
#         }.items()
#
#     def __str__(self):
#         return json.dumps(dict(self), ensure_ascii=False)
#
#     def __repr__(self):
#         return self.__str__()
#
#
# class MyEncoder(JSONEncoder):
#     def default(self, obj):
#         return obj.__dict__

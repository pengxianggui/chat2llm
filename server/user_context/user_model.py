from pydantic import BaseModel


class User(BaseModel):
    client_id: str
    user_id: str
    username: str
    enable: bool

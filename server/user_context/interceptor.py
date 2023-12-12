from binascii import Error

from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from server.auth import decrypt
from server.db.repository import get_user, add_user
from server.user_context.user_model import User

api_token_key = 'Api-Token'
api_token_header = APIKeyHeader(name=api_token_key, auto_error=False)


# 类似于java的interceptor
class TokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_token = request.headers.get(api_token_key)

        # 如果c_token为空，则直接放行。防止一些无需认证的接口被控制(比如/docs)
        if not api_token:
            return await call_next(request)

        try:
            client_id, user_id, username = decrypt(api_token)
            if not client_id or not user_id:
                # 在middleware中抛出此401异常没用，前端收到的始终是500
                # await HTTPException(status_code=401, detail=f"Authentication required: {api_token_key} is invalid!")
                return Response(status_code=401, content=f"Authentication required: {api_token_key} is invalid!")

            user = get_user(client_id, user_id)
            if user is None:
                user = add_user(client_id, user_id, username)

            request.state.user = User(client_id=user.client_id, user_id=user.user_id, username=user.username,
                                      enable=user.enable)
        except Error:
            return Response(status_code=401, content=f"Authentication required: {api_token_key} is invalid!")

        return await call_next(request)


# 自定义的依赖注入，在注入的方法调用前会执行。
async def get_current_user(request: Request, api_token: str = Security(api_token_header)):
    if not api_token:
        raise HTTPException(status_code=401, detail=f"Authentication required: miss {api_token_key}!")

    try:
        return request.state.user
    except AttributeError:
        raise HTTPException(status_code=401, detail=f"Authentication required: {api_token_key} is invalid!")

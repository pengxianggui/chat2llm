import time

from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from configs import TOKEN_EXPIRED_HOURS, API_TOKEN_KEY
from server.auth import decrypt
from server.db.repository import get_user, add_user

api_token_header = APIKeyHeader(name=API_TOKEN_KEY, auto_error=False)


# 类似于java的interceptor
class TokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_token = request.headers.get(API_TOKEN_KEY)

        # 如果c_token为空，则直接放行。防止一些无需认证的接口被控制(比如/docs)
        if not api_token:
            return await call_next(request)

        try:
            client_id, user_id, username, timestamp = decrypt(api_token)
            if not client_id or not user_id:
                # 在middleware中抛出此401异常没用，前端收到的始终是500
                return Response(status_code=401, content=f"Authentication required: {API_TOKEN_KEY}无效!")

            diff_hours = (time.time() - timestamp) / 3600
            if diff_hours > float(TOKEN_EXPIRED_HOURS):
                return Response(status_code=401, content=f"Authentication required: token过期!")

            user = get_user(client_id, user_id)
            if user is None:
                user = add_user(client_id, user_id, username)

            request.state.user = user
        except Exception as e:
            return Response(status_code=401, content=f"Authentication required: {API_TOKEN_KEY}无效!")

        return await call_next(request)


# 自定义的依赖注入，在注入的方法调用前会执行。
async def get_current_user(request: Request, api_token: str = Security(api_token_header)):
    if not api_token:
        raise HTTPException(status_code=401, detail=f"Authentication required: 缺少{API_TOKEN_KEY}!")

    try:
        return request.state.user
    except AttributeError:
        raise HTTPException(status_code=401, detail=f"Authentication required: {API_TOKEN_KEY}无效!")

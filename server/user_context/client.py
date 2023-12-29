from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from configs import H5_DEMO_SECRET, H5_ADDRESS
from server.auth import generate_rsa_keys, encrypt
from server.db.repository import get_client, add_client, get_user, add_user


# 重定向到h5 demo页面。
def redirect_h5_demo(secret: str, request: Request):
    if secret != H5_DEMO_SECRET:
        raise HTTPException(status_code=401, detail=f"Authentication required: 口令错误!")

    default_client_id = "0"
    client = get_client(default_client_id)  # 获取默认的client
    if client is None:
        client_secret, client_key = generate_rsa_keys()
        client = add_client(default_client_id, client_key, client_secret, "默认客户端, 用于h5 demo——直接浏览器访问h5。")

    ip = request.client.host
    user = get_user(client.id, ip)
    if user is None:
        user = add_user(client.id, ip, ip)

    token = encrypt(client.id, user.user_id, user.user_id)
    return RedirectResponse(url=H5_ADDRESS + "?token=" + token)





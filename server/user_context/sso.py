import os
from urllib import parse
from typing import Union

from fastapi import Query
from starlette.requests import Request
from starlette.responses import RedirectResponse

from configs import H5_DEMO_SECRET, H5_ADDRESS, SERVER_ADDRESS, ENT_WECHAT_CORPID, ENT_WECHAT_AGENTID
from server.auth import generate_rsa_keys, encrypt
from server.db.repository import get_client, add_client, get_user, add_user
from server.third.ent_wechat import get_ent_chat_user


# 统一单点登录处理接口
def sso_handler(client: Union[str, None] = Query(default="0", description="客户端id，必须是系统支持的，用以声明h5环境。默认是0表示浏览器环境"),
                secret: Union[str, None] = Query(default=None, description="当client为0时必传"),
                redirect_url: Union[str, None] = Query(default=None, description="当需要指定重定向时可传入。通常用于本地h5连接"),
                request: Request = None):
    if redirect_url is None:
        redirect_url = H5_ADDRESS

    if client is None:
        return RedirectResponse(url=f"{redirect_url}/401?message=未知客户端,无法单点登录,请重新进入。")

    if client == "0":  # h5演示页面
        return redirect_h5_demo(secret, redirect_url, request)
    if client == "1":  # 企微页面
        REDIRECT_URI = parse.quote(SERVER_ADDRESS + "/ent-wechat-sso")
        return RedirectResponse(url=f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={ENT_WECHAT_CORPID}"
                                    f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=snsapi_privateinfo"
                                    f"&state={client}&agentid={ENT_WECHAT_AGENTID}#wechat_redirect")

    return RedirectResponse(url=f"{redirect_url}/401?message=无效的客户端,无法单点登录,请重新进入")


# 重定向到h5 demo页面。
def redirect_h5_demo(secret: str, redirect_url: str, request: Request):
    if secret != H5_DEMO_SECRET:
        return RedirectResponse(url=f"{redirect_url}/401?message=单点失败, 请提供正确口令")

    client_id = 0  # h5演示页面默认的client
    client = get_client(client_id)  # 获取默认的client
    if client is None:
        client_secret, client_key = generate_rsa_keys()
        client = add_client(client_id, client_key, client_secret, "默认客户端, 用于h5 demo——直接浏览器访问h5。")

    ip = request.client.host
    user = get_user(client.id, ip)
    if user is None:
        user = add_user(client.id, ip, ip)

    token = encrypt(client.id, user.user_id, user.user_id)
    redirect_to = f"{redirect_url}/sso?token={token}"
    print(f"redirect to {redirect_to}")
    return RedirectResponse(url=redirect_to)


# 企微单点回调
def ent_wechat_sso(code: str, state: str):
    print(f"receive ent wechat sso callback, code: {code}")
    if code is None or len(code) == 0:
        return RedirectResponse(url=f"{H5_ADDRESS}/401?message=参数错误")

    client_id = state
    client = get_client(client_id)  # 获取默认的client
    if client is None:
        return RedirectResponse(url=f"{H5_ADDRESS}/401?message=拒绝访问, 未知客户端: {client_id}")

    # 根据code获取企微用户信息，并根据系统中的RSA进行加密生成token并重定向前端
    try:
        user_id, username = get_ent_chat_user(code)
        user = get_user(client.id, user_id)
        if user is None:
            print(f"detect current user is newer, add to db..")
            user = add_user(client.id, user_id, username)
        token = encrypt(client.id, user.user_id, user.username)
        return RedirectResponse(url=f"{H5_ADDRESS}/sso?token={token}")
    except RuntimeError as e:
        print(e)
        return RedirectResponse(url=f"{H5_ADDRESS}/401?message=获取用户信息失败:{e}")

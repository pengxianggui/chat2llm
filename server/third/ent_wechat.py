import requests
from cachetools.func import ttl_cache

from configs import ENT_WECHAT_CORPID, ENT_WECHAT_APPSECRET


# 根据code获取企微用户信息
def get_ent_chat_user(code: str):
    data = get_user_info_simple(code)
    user_id = data['userid']
    if user_id is None: # 可能是非企业成员, 见: https://developer.work.weixin.qq.com/document/path/91023
        return data['openid'], data['openid']  # 则将openid视为user_id和username
    else:
        return user_id, user_id


# 获取accessToken: https://developer.work.weixin.qq.com/document/path/91039#15074
@ttl_cache(ttl=7200)
def get_access_token():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        'corpid': ENT_WECHAT_CORPID,
        'corpsecret': ENT_WECHAT_APPSECRET
    }
    response = requests.get(url, params=params)
    data = response.json()
    errcode = data['errcode']
    if errcode != 0:
        errmsg = data['errmsg']
        raise RuntimeError(errmsg)
    else:
        return data['access_token']


# 获取用户身份: https://developer.work.weixin.qq.com/document/path/91023
def get_user_info_simple(code: str):
    accessToken = get_access_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo"
    # 根据code获取企微用户信息
    params = {
        'access_token': accessToken,
        'code': code
    }
    response = requests.get(url, params=params)
    data = response.json()
    errcode = data['errcode']
    if errcode != 0:
        errmsg = data['errmsg']
        raise RuntimeError(errmsg)
    else:
        return data

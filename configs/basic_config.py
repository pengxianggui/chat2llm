import logging
import os
import langchain


# 是否显示详细日志
log_verbose = False
langchain.verbose = False

# 是否启用爱助手LLM代理: 若启用爱助手代理，则LLM功能将走爱助手接口，而不是longchain代理的第三方LLM开放接口。对话、知识库对话以及知识库列表都将走爱助手接口。
ENABLE_AZS = os.environ.get("ENABLE_AZS", True)
AZS_URL = os.environ.get("AZS_URL", "https://ai.marssenger.cn/api/open-api")  # 爱助手的接口地址, 若ENABLE_AZS=True时有效
AZS_APP_SECRET = os.environ.get("AZS_APP_SECRET", "")  # 爱助手的接口认证的appSecret, 若ENABLE_AZS=True时有效
# 是否保存聊天记录
SAVE_CHAT_HISTORY = True

# api访问token有效期
TOKEN_EXPIRED_HOURS = os.environ.get("TOKEN_EXPIRED_HOURS", 8)
# the key of token in header
API_TOKEN_KEY = 'Api-Token'

# 当前服务端地址
SERVER_ADDRESS = os.environ.get("SERVER_ADDRESS", "http://127.0.0.1:7861")
# h5的开放地址
H5_ADDRESS = os.environ.get("H5_ADDRESS", "http://127.0.0.1:8080")

# 企微应用配置
ENT_WECHAT_AGENTID = os.environ.get("ENT_WECHAT_AGENTID")
ENT_WECHAT_CORPID = os.environ.get("ENT_WECHAT_CORPID")
ENT_WECHAT_APPSECRET = os.environ.get("ENT_WECHAT_APPSECRET")

# 通常情况下不需要更改以下内容

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)


# 日志存储路径
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

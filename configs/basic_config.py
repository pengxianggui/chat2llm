import logging
import os
import langchain


# 是否显示详细日志
log_verbose = False
langchain.verbose = False

# 是否保存聊天记录
SAVE_CHAT_HISTORY = True

# api访问token有效期
TOKEN_EXPIRED_HOURS = 8
# the key of token in header
API_TOKEN_KEY = 'Api-Token'

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

# Chat2LLM-Server
> Chat2LLM是和大语言模型(LLM)对话的项目，利用这个项目，可以落地一些AI应用场景, 如知识库，智能客服。

这是项目的服务端，基于开源项目[LangChain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat)的[0.2.7](https://github.com/chatchat-space/Langchain-Chatchat/tree/v0.2.7)版本。
已经实现基本的服务端功能。

关于原项目的介绍，如果上面github访问慢，还可以查看项目中的原[readme文件](./README_origin.md)。

## 功能
- [x] 实现真正与LLM对话。
- [x] 实现文件向量化并入库(文件形式)。
- [x] 绝大部分的API接口。
- [x] 实现访问认证控制。

## 技术栈
- python: 3.10.11+, 推荐3.10.12
- pip: 23.0.1


## 关于工程的一点理解
> github上的readme和wiki还是比较详细的，这里只是记录一点自己摸索过程的一点心得。

1. python一定要符合版本要求，最好就用3.10.12。我用的3.10.11也吭哧吭哧捣鼓成功了。
2. 最多坑的地方是`pip install`阶段，网络问题引起的也好，源引起的也好，总之会遇到很多问题，有时一两个包下载失败，过后可能又正常下载。
3. 文件向量化阶段也容易出问题，千万别忘记初始化向量库。
4. 以`--lite`轻量形式跑，可以不用本地化部署大语言模型，而是使用一些厂家的开放API(如openai, 智谱、讯飞等)，因此需要提前注册并生成api-key来配上。
5. 虽然轻量形式跑无需部署LLM, 但是如果涉及知识库功能，仍然需要涉及一些自然语言处理模型(比如模型m3e-base等)，所以依然对内存有点要求。
具体数值没测过，之前16G，偶尔python内存不足退出，后来升级到24G, 似乎没有遇到过了。
6. 如果涉及知识库功能，需要本地跑一些模型，这些模型在项目里是不带的，运行是会自动从huggingface下载，不幸的是它不久前被墙了，不过可以翻墙下载下来后
放到本地目录去。为避免项目过大，我没把下下来的模型放仓库。


## 待办
- [x] 用户、终端认证
- [x] 知识库列表接口追加返回描述信息和知识库中文名
- [ ] 解决对话带有history时, 几轮对话下来会触发报错: [utils.py[line:25] - ERROR: TypeError: Caught exception: object of type 'NoneType' has no len()](https://github.com/chatchat-space/Langchain-Chatchat/issues/2228)
- [x] 增加会话等数据的持久化
- [ ] 命令行支持 --config config.ini 指定配置文件完整路径


## 关于认证
由于不打算提供自己的用户体系，外部来源的用户体系又不止一个。因此采用RSA非对称加密方式认证和识别客户端和用户。即通过请求头携带`api_token`实现认证。

> 这里阐述下具体逻辑:
> 
> 例如h5页面计划嵌入到企微的某个小程序A里, 那么需要在Chat2LLM中为A添加一个client记录，包含的字段有: client_id, client_key, client_secret(公钥和密钥由Chat2LLM server生成)。
> 小程序A在嵌入h5页面时, url地址参数里携带一个api_token。H5内部的所有请求都会携带api_token, Chat2LLM server 通过api_token识别client。
> 
> A如何生成api_token: 根据颁发的公钥client_key, 通过RSA加密字符串: "client_id|user_id|username|timestamp", 得到A, 然后通过base64加密"client_id|A", 从而生成api_token。
> 
> Chat2LLM Server如何解密api_token: 首先通过base64解密得到client_id和A, 再通过client_id找到对应的私钥，通过私钥client_secret解密A, 从而得到当前请求的client_id、user_id和username。
> 顺利解析，并且client_id合法，则放行(若user_id库里不存在，则新增此用户)。否则响应拒绝。

需要对数据库表做如下调整:
1. 新增client表: id, client_key, client_secret, description, enable;
2. 新增user表: client_id, user_id, username, enable;

关于演示和调试: 以上策略也会导致直接访问h5页面(无有效api_token)时, 无法访问。因此可采取后端提供一个demo演示接口，重定向到一个h5地址，并附带后端
生成的api_token即可，这个api_token是通过内置的demo_client生成。
> 这个demo演示接口可以通过口令简单校验。

## 关于会话的持久化
通过client_id + user_id确定用户。因此, 需要对数据库表做如下调整:
1. 新增chat_session表: id, client_id, user_id, mode, session_name, param
2. 调整chat_history表: 增加字段(session_id, docs), id值采用前端提供的值


## 关于部署
config.ini里有所有的环境变量覆盖配置项，部署时需保证此文件在项目根目录(暂时不支持命令行指定目录)。
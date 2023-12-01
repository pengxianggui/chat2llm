# Chat2LLM-Server
> Chat2LLM是和大语言模型(LLM)对话的项目，利用这个项目，可以落地一些AI应用场景, 如知识库，智能客服。

这是项目的服务端，基于开源项目[LangChain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat)的[0.2.7](https://github.com/chatchat-space/Langchain-Chatchat/tree/v0.2.7)版本。
已经实现基本的服务端功能。

关于原项目的介绍，如果上面github访问慢，还可以查看项目中的原[readme文件](./README_origin.md)。

## 功能
- [x] 实现真正与LLM对话。
- [x] 实现文件向量化并入库(文件形式)。
- [x] 绝大部分的API接口。
- [ ] 实现访问认证控制。

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
- [ ] 用户、终端认证
- [ ] 知识库列表接口追加返回描述信息和知识库中文名
- [ ] 解决对话带有history时, 几轮对话下来会触发报错: [utils.py[line:25] - ERROR: TypeError: Caught exception: object of type 'NoneType' has no len()](https://github.com/chatchat-space/Langchain-Chatchat/issues/2228)
- [ ] 增加mysql存储功能，存储数据: 会话、知识库中文名等内容。
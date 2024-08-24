import asyncio
import json

import requests

# 爱助手测试env
# url = "https://ai.enterpriseai.com.cn/api/open-api"
# api_key = "93e03624046044ba8ea6973dd124fc0f"

# 我们的
url = "https://ai.marssenger.cn/api/open-api"
api_key = "ec9df637b3724a7a9d7a2b64eb37f3ba"

# 获取知识库列表，接口文档: https://ai.enterpriseai.com.cn/help/zh/api/openApi%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.html#_2-%E8%8E%B7%E5%8F%96%E7%9F%A5%E8%AF%86%E5%BA%93%E5%88%97%E8%A1%A8
def list_kbs_from_azs(keyword: str, num: int):
    headers = {
        "App-Secret": api_key,
        "content-Type": "application/json; charset=utf-8"
    }
    data = {
        "keyword": keyword
    }
    response = requests.post(url + "/v2/kb-list", json=data, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        data = []
        kbs = response_data.get("data")
        if kbs:
            for kb in kbs:
                data.append({
                    "kb_id": kb.get("id"),
                    "kb_name": kb.get("name"),
                    "kb_zh_name": kb.get("name"),
                    "kb_info": kb.get("welcomeText"),
                    "vs_type": None,
                    "embed_model": kb.get("llmModel"),
                    "file_count": kb.get("docCount"),
                    "create_time": None,
                })
                if num is not None and len(data) >= num:
                    break
        return data
    return []


# 流式问答
async def fetch_with_streaming(path: str, params, chat_history_id: str, queue: asyncio.Queue):
    headers = {
        "App-Secret": api_key,
        "content-Type": "application/json; charset=utf-8"
    }

    loop = asyncio.get_event_loop()

    def decode_streaming_data(response):
        received_buffer = ""
        for chunk in response.iter_content(chunk_size=512):
            decoded_chunk = chunk.decode('utf-8')
            received_buffer += decoded_chunk
            received_buffer = resolve_streaming_data(received_buffer)

    def resolve_streaming_data(received_buffer):
        lines = received_buffer.split("\n")
        last_line = lines.pop()
        for line in lines:
            json_value = json.loads(line)
            loop.call_soon_threadsafe(queue.put_nowait, json.dumps({
                "text": json_value.get('content', ''),
                "chat_history_id": chat_history_id
            }, ensure_ascii=False))
        try:
            if last_line:
                last_value = json.loads(last_line)
                loop.call_soon_threadsafe(queue.put_nowait, json.dumps({
                    "text": last_value.get('content', ''),
                    "chat_history_id": chat_history_id
                }, ensure_ascii=False))
        except Exception as e:
            print(f"流式输出遇到异常：{e}")
            return last_line
        return ""

    # 在后台线程中执行同步的requests操作
    with requests.post(url + path, json=params, headers=headers, stream=True) as response:
        response.raise_for_status()
        await loop.run_in_executor(None, decode_streaming_data, response)

    await queue.put(None)  # 结束信号

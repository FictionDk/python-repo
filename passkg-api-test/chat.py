import requests
import json


def chat_stream(
    workspace_id: str,
    message: str,
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    """
    向指定的 workspace 发送消息，并通过 text/event-stream 协议接收流式响应。
    
    参数:
        workspace_id (str): 目标 workspace 的 ID（必填）
        message (str): 要发送的消息内容（必填）
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        None: 此函数直接打印流式响应，不返回值。
    """
    url = f"{base_url}/chat/{workspace_id}"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return
    
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json"
    }
    data = {
        "message": message
    }
    
    try:
        # 使用 stream=True 来处理流式响应
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return
        
        # 检查 Content-Type 是否为 text/event-stream
        content_type = response.headers.get('Content-Type', '')
        if 'text/event-stream' not in content_type:
            print(f"⚠️  警告：预期的 Content-Type 为 text/event-stream，但收到的是 {content_type}")
        
        # 逐行迭代流式响应
        for line in response.iter_lines():
            # 忽略空行
            if line:
                # 将字节行解码为字符串
                decoded_line = line.decode('utf-8')
                # 打印原始的事件流行
                # print(decoded_line)
                #（可选）可以在这里解析以 "data:" 开头的行
                if decoded_line.startswith("data:"):
                    data_content = decoded_line[5:].strip()
                    if data_content == "[DONE]":
                        print("✅ 流式响应结束")
                        break
                    else:
                        # 处理数据内容
                        #print(f"接收到数据: {data_content}")
                        print(f"{json.loads(data_content)['message']}",end="")
                
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
    except Exception as e:
        print(f"⚠️ 发生未知错误: {e}")

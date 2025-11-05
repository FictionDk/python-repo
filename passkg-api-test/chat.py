import requests
import json
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

LLM_TEMPERATURE = 0.7
LLM_TOP_P = 1
LLM_STREAM = True

def interactive_chat(
    workspace_id: str,
    base_url: str = "http://localhost:8080",
    jwt: str = None,
    is_llm: bool = False
):
    """
    启动一个交互式聊天会话，持续读取用户输入并发送消息到指定 workspace，
    直到用户输入 'exit' 为止。

    参数:
        workspace_id (str): 目标 workspace 的 ID（必填）
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    """
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return

    print(f"🚀 启动交互式聊天会话，连接到 workspace: {workspace_id}")
    print("输入消息开始聊天，输入 'exit' 退出。\n")

    # 初始化消息历史记录
    messages = []

    while True:
        try:
            # 读取用户输入
            user_input = input("💬 你: ").strip()
            
            # 检查是否退出
            if user_input.lower() == 'exit':
                print("👋 聊天结束，再见！")
                return messages

            # 将用户消息添加到历史记录
            messages.append({"role": "user", "content": user_input, "workspaceId": workspace_id, "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            # 调用 chat_stream 发送完整的消息历史
            assistant_response = chat_stream(workspace_id=workspace_id, messages=messages, base_url=base_url, jwt=jwt, is_llm=is_llm)
            
            # 将助手的回复添加到历史记录
            if assistant_response:
                messages.append({"role": "assistant", "content": assistant_response, "workspaceId": workspace_id, "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            else:
                # 如果请求失败，移除最后一条用户消息以保持历史一致
                messages.pop()

            print()  # 换行，分隔不同消息的输出

        except KeyboardInterrupt:
            print("\n\n� 聊天被中断，再见！")
            return messages
        except Exception as e:
            print(f"⚠️  发生错误: {e}")
            return messages


def push(
    workspace_id: str,
    messages: list,
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    """
    将聊天历史记录 messages 列表推送到指定的 workspace 的日志接口。
    
    参数:
        workspace_id (str): 目标 workspace 的 ID（必填）
        messages (list): 消息列表，每个消息为 {"role": "user"|"assistant", "content": "内容", "workspaceId": "workspace_id", "createdAt": "timestamp"}
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        bool: 推送成功返回 True，否则返回 False。
    """
    url = f"{base_url}/chat/logs/{workspace_id}"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return False
    
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json"
    }
    data = {
        "logs": messages
    }
    print(f"messages: {messages}")
    
    try:
        response = requests.post(url, headers=headers, json=messages)
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ 聊天历史记录已成功推送到 workspace: {workspace_id}")
            return True
        else:
            print(f"❌ 推送失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return False


def get_logs(
    workspace_id: str,
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    """
    从指定的 workspace 的日志接口获取消息列表。
    
    参数:
        workspace_id (str): 目标 workspace 的 ID（必填）
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        list: 返回获取到的消息列表，失败返回 None。
    """
    url = f"{base_url}/chat/logs/{workspace_id}"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    
    headers = {
        "Authorization": f"Bearer {jwt}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ 成功从 workspace: {workspace_id} 获取消息列表")
            return response.json()
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None


def chat_stream(
    workspace_id: str,
    messages: list,
    base_url: str = "http://localhost:8080",
    jwt: str = None,
    is_llm: bool = False
):
    """
    向指定的 workspace 发送消息列表，并通过 text/event-stream 协议接收流式响应。
    
    参数:
        workspace_id (str): 目标 workspace 的 ID（必填）
        messages (list): 消息列表，每个消息为 {"role": "user"|"assistant", "content": "内容"}
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        str: 返回模型的完整响应内容，用于更新本地历史记录。
    """
    url = base_url
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return ""
    if is_llm:
        data = {
            "messages": messages,
            "model": os.getenv("LLM_MODEL"),
            "temperature": LLM_TEMPERATURE,
            "top_p": LLM_TOP_P,
            "stream": LLM_STREAM,
            "stop": None,
        }
    else:
        url = f"{base_url}/chat/{workspace_id}"
        data = {
            "messages": messages
        }
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json"
    }
    try:
        # 使用 stream=True 来处理流式响应
        response = requests.post(url, headers=headers, json=data, stream=LLM_STREAM)
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
        full_response = ""
        for line in response.iter_lines():
            # 忽略空行
            if line:
                # 将字节行解码为字符串
                decoded_line = line.decode('utf-8')
                #（可选）可以在这里解析以 "data:" 开头的行
                if decoded_line.startswith("data:"):
                    data_content = decoded_line[5:].strip()
                    if data_content == "[DONE]":
                        print("✅ 流式响应结束")
                        break
                    else:
                        # 处理数据内容
                        r_json = json.loads(data_content)
                        message_data = ""
                        if is_llm:
                            message_data = r_json["choices"][0]["delta"]["content"]
                        else:
                            is_end = r_json["isEnd"]
                            if is_end:
                                print(f"{r_json['message']}{r_json['ref']}")
                            else:
                                message_data = r_json['message']
                        print(f"{message_data}", end="")
                        full_response += message_data

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return ""
    except Exception as e:
        print(f"⚠️ 发生未知错误: {e}")
        return ""
    
    return full_response

#interactive_chat(workspace_id="", jwt=os.getenv('LLM_API_KEY'), base_url=os.getenv("LLM_API_URL"), is_llm=True)

jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGFzZXMiOiLnrqHnkIblkZgiLCJleHAiOjE3NjE5MDM2MDUsImlhdCI6MTc2MTg5NjQwNSwicm9sZSI6IuWQjuWPsOeuoeeQhiIsInVzZXJuYW1lIjoiYWRtaW4ifQ.E0hJSqXl7MFX3hhkSuBGbTTCwkyS33mvRB4KsiPpfhw'
interactive_chat(workspace_id="cowherd", jwt=jwt, base_url='http://192.168.98.11:8080')
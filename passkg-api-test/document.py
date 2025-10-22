import requests
import os


def process_document(document_id: str, 
                     prompt_id: str = "9b6f9f92-dafb-495f-acf8-b2b7cac2ce44", 
                     base_url: str = "http://localhost:8080",
                     jwt: str = None):
    url = f"{base_url}/documents/{document_id}/process"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    try:
        response = requests.post(url, json={"promptId":prompt_id}, headers=headers)
        if response.status_code == 202:
            print("✅ 文档处理提交成功！")
            return response.json()
        else:
            print(f"❌ 创建失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None

def create_document_in_workspace(
    workspace_id: str,
    name: str,
    content: str = "",
    summary: str = "",
    tags: list = None,
    parent: str = None,
    extraction_prompt: str = "",
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    """
    为指定 workspace 创建一篇文档。
    参数:
        workspace_id (str): 所属 workspace 的 ID
        name (str): 文档名称（必填）
        content (str): 文档内容。如果为文件路径，则自动读取文件内容。
        summary (str): 摘要
        tags (list): 标签列表
        parent (str): 父文档 ID（可选）
        extraction_prompt (str): 提取 prompt（可选）
        base_url (str): API 地址
        jwt (str): JWT 认证令牌（可选）
    返回:
        dict: 创建的文档对象，失败返回 None
    """
    # 如果 content 是文件路径，则读取文件内容
    if content and os.path.isfile(content):
        try:
            with open(content, 'r', encoding='utf-8') as file:
                file_content = file.read()
            print(f"✅ 成功读取文件内容: {content}")
            content = file_content
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return None

    url = f"{base_url}/documents"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    payload = {
        "workspaceID": workspace_id,
        "name": name,
        "content": content,
        "summary": summary,
        "tags": tags or [],
        "parent": parent,
        "extractionPrompt": extraction_prompt
        # 其他字段如 type, processStatus 等可由后端默认生成
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print("✅ 文档创建成功！")
            return response.json()
        else:
            print(f"❌ 创建失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None

def get_docs(workspace_id: str = "cowherd",
             base_url: str = "http://localhost:8080",
             jwt: str = None) -> list[dict[str, any]]:
    """
    获取指定 workspace 中的所有文档列表。
    
    参数:
        workspace_id (str): workspace 的 ID，默认为 "cowherd"
        base_url (str): API 地址，默认为 "http://localhost:8080"
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        list[dict]: 文档对象列表，每个文档为字典格式，失败返回 None
    """
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
        
    url = f"{base_url}/workspaces/{workspace_id}/documents"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ 成功获取文档列表！")
            return response.json()
        else:
            print(f"❌ 获取文档列表失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None


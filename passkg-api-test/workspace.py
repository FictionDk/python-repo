import requests

def create_workspace(
    name,
    description="",
    retrieval_model="default-model",
    search_depth=5,
    max_entities=20,
    max_chunks=5,
    base_url="http://localhost:8080",
    jwt: str = None
):
    """
    创建一个新的 workspace。
    参数:
        name (str): workspace 名称（必填）
        description (str): 描述
        retrieval_model (str): 检索模型名称
        search_depth (int): 搜索深度，默认 5
        max_entities (int): 最大实体数，默认 20
        max_chunks (int): 最大 chunk 数，默认 5
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    返回:
        dict: 响应 JSON 数据，包含创建的 workspace 信息或错误
    """
    url = f"{base_url}/workspaces"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    payload = {
        "name": name,
        "description": description,
        "retrievalModel": retrieval_model,
        "searchDepth": search_depth,
        "maxEntities": max_entities,
        "maxChunks": max_chunks
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print("✅ Workspace 创建成功！")
            return response.json()
        else:
            print(f"❌ 创建失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None


def set_workspace_model_config(
    workspace_id: str,
    models: list,
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    """
    为空间设置不同类别的模型配置。由于POST接口一次只能推送一个task，
    因此会循环处理models列表中的每个模型配置。
    
    参数:
        workspace_id (str): workspace ID（必填）
        models (list): 模型配置列表，每个配置包含 task 和 model 字段
            示例: [
                {"task": "Reasoning", "model": "gpt-4"},
                {"task": "ImageToText", "model": "vit-large"},
                {"task": "Audio2Text", "model": "whisper-large"},
                {"task": "Extraction", "model": "bert-extractor"},
                {"task": "Embedding", "model": "bge-m3"},
                {"task": "Reranking", "model": "bge-reranker"}
            ]
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        dict: 包含所有请求结果的字典，包括成功和失败的信息
    """
    url = f"{base_url}/workspacemodels/{workspace_id}"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    
    results = {
        "success": [],
        "failed": [],
        "workspace_id": workspace_id
    }

    for model_config in models:
        payload = model_config
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201, 204]:
                print(f"✅ 模型配置设置成功！任务: {model_config['task']}, 模型: {model_config['model']}")
                results["success"].append({
                    "task": model_config["task"],
                    "model": model_config["model"],
                    "status": response.status_code,
                    "response": response.json() if response.content else {}
                })
            else:
                print(f"❌ 配置失败，状态码: {response.status_code}，任务: {model_config['task']}")
                print(f"错误信息: {response.text}")
                results["failed"].append({
                    "task": model_config["task"],
                    "model": model_config["model"],
                    "status": response.status_code,
                    "error": response.text
                })
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 网络请求出错: {e}，任务: {model_config['task']}")
            results["failed"].append({
                "task": model_config["task"],
                "model": model_config["model"],
                "error": str(e)
            })
    
    # 如果所有请求都成功，返回第一个成功的响应内容
    if not results["failed"] and results["success"]:
        return results["success"][0]["response"]
    # 如果有失败的请求，返回完整的结果详情
    else:
        return results

def get_workspace_model_config(
    workspace_id: str,
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    """
    获取指定空间的模型配置。
    
    参数:
        workspace_id (str): workspace ID
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        dict: 模型配置信息，失败返回 None
    """
    url = f"{base_url}/workspacemodels/{workspace_id}"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    headers = {
        "Authorization": f"Bearer {jwt}"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ 成功获取模型配置")
            return response.json()
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None


def get_workspace_members(
    workspace_id: str,
    jwt: str,
    base_url: str = "http://localhost:8080"
):
    """
    获取指定 workspace 的成员列表。
    
    参数:
        workspace_id (str): workspace ID（必填）
        base_url (str): API 基地址
    
    返回:
        list[str]: 成员用户名列表，失败返回 None
    """
    url = f"{base_url}/workspaces/{workspace_id}/members"
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + jwt})
        if response.status_code == 200:
            members = response.json()
            print(f"✅ 成功获取 {len(members)} 个成员")
            return members
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None


def retrieve_naive(
    query: str,
    workspace_id: str,
    jwt: str,
    base_url: str = "http://localhost:8080",
):
    """
    对指定 workspace 执行朴素检索查询。
    
    参数:
        query (str): 检索查询字符串（必填）
        workspace_id (str): workspace ID（必填）
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        dict: 检索结果 JSON 数据，失败返回 None
    """
    url = f"{base_url}/retrieve/naive"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    payload = {
        "query": query,
        "workspace_id": workspace_id
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ 朴素检索查询成功！")
            return response.json()
        else:
            print(f"❌ 检索失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None

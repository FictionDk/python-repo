import requests
import logging

# Configure logging
logger = logging.getLogger(__name__)

def post(workspace_id: str, data: dict, batch_size: int = 1000, base_url: str = "http://localhost:8080"):
    """
    Post entities and relations data to the remote batch import API.

    Args:
        workspace_id (str): The ID of the workspace.
        data (dict): The data dictionary containing 'entities' and 'relations' lists.
                     Expected format:
                     {
                         'entities': [...],
                         'relations': [...]
                     }
        batch_size (int, optional): The batch size for the import. Defaults to 100.
        base_url (str, optional): The base URL of the API. Defaults to "http://localhost:8080".

    Returns:
        bool: True if the import was successful (HTTP 200), False otherwise.
    """
    jwt = login('admin', 'stpass', base_url=base_url)
    url = f"{base_url}/workspaces/{workspace_id}/graph/batch-import"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt}"
    }
    payload = {
        "entities": data.get("entities", []),
        "relations": data.get("relations", []),
        "batch_size": batch_size
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result : dict = response.json()
            logger.info(f"Batch import successful: {result.get('message', 'Import completed')}. "
                       f"Imported {result.get('imported_entities', 0)} entities and "
                       f"{result.get('imported_relations', 0)} relations.")
            return True
        else:
            logger.error(f"Batch import failed with status code {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during batch import: {e}")
        return False

def login(usr, pwd, base_url="http://localhost:8080"):
    """
    测试登录接口
    POST xxx:8080/login body={username=admin,password=stpass}
    响应体为jwt
    """
    url = f"{base_url}/login"
    payload = {"username": usr,"password": pwd}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            jwt_token = result['token']
            return jwt_token
        else:
            print(f"登录失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求出错: {e}")
        return None

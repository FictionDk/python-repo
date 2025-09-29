import requests
import os


def upload_image_to_workspace(
    workspace_id: str,
    image_path: str,
    base_url: str = "http://localhost:8080",
    jwt: str = None
):
    """
    将本地图片文件上传到指定的 workspace。
    
    参数:
        workspace_id (str): 目标 workspace 的 ID（必填）
        image_path (str): 本地图片文件的路径（必填）
        base_url (str): API 基地址
        jwt (str): JWT 认证令牌（必传）
    
    返回:
        dict: 上传成功时返回响应 JSON 数据，失败返回 None
    """
    url = f"{base_url}/api/workspaces/{workspace_id}/upload/image"
    if not jwt:
        print("❌ 错误：jwt 认证令牌为必传参数")
        return None
    if not os.path.isfile(image_path):
        print(f"❌ 错误：文件不存在 - {image_path}")
        return None

    headers = {
        "Authorization": f"Bearer {jwt}"
    }
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {'file': (os.path.basename(image_path), image_file, 'image/jpeg')}
            response = requests.post(url, files=files, headers=headers)
        
        if response.status_code == 200:
            print("✅ 图片上传成功！")
            return response.json()
        else:
            print(f"❌ 上传失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None
    except Exception as e:
        print(f"⚠️ 文件操作出错: {e}")
        return None

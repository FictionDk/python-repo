import requests

BASE_URL = "http://localhost:18080" 
WORKSPACE_ID = "itfach"
FILE_PATH = "./graph-export-itfach.json"

token =  "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGFzZXMiOiLnrqHnkIblkZgiLCJleHAiOjE3NzA2MTM5ODUsImlhdCI6MTc3MDYwNjc4NSwicm9sZSI6InVzZXIiLCJ1c2VyX2lkIjoiYWRtaW4iLCJ1c2VybmFtZSI6ImFkbWluIn0.1zGEwmsog-P72tW4KDu1hLGozX6Dlt-zMupF4gC3WOw"
# authorization
def upload_file():
    # 1. 构建完整的 URL
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/import-binary"

    # 2. 打开文件
    # 注意：必须使用 'rb' (二进制读取) 模式
    with open(FILE_PATH, 'rb') as f:
        # 3. 构建 files 字典
        # 这里的 'file' 对应前端 formData.append('file', file) 中的第一个参数（字段名）
        # 元组格式 ('filename', fileobj) 是推荐写法，以确保后端能正确识别文件名
        files = {
            'file': (FILE_PATH.split('/')[-1], f)
        }

        # 4. 发送请求
        try:
            # 对应前端的 300000ms (5分钟)，requests 的 timeout 单位是秒，所以设为 300
            response = requests.post(
                url, 
                files=files,
                headers={"Authorization": token},
                timeout=1200
            )

            # 5. 处理响应
            if response.status_code == 200:
                print("上传成功:", response.json())
            else:
                print(f"上传失败，状态码: {response.status_code}")
                print("错误信息:", response.text)

        except requests.exceptions.Timeout:
            print("请求超时")
        except requests.exceptions.RequestException as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    upload_file()

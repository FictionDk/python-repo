import requests

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
            jwt_token = response.json()['token']
            print(f"✅ 登录成功")
            return jwt_token
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None

def list_users(jwt, base_url="http://localhost:8080"):
    url = f"{base_url}/users"
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + jwt})
        if response.status_code == 200:
            users = response.json()['users']
            print(users)
            print(f"✅ 成功获取 {len(users)} 个用户列表")
            return users
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None
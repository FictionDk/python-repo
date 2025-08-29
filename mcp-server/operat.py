from mcp.server.fastmcp import FastMCP
import requests
from typing import Tuple

mcp = FastMCP("Operator", log_level="ERROR")
API_TOKEN = "YOUR_API_KEY"  # 初始占位符

def handle_login():
    """处理登录认证并获取API令牌"""
    global API_TOKEN
    login_url = "http://imes.dev.uplasm.com/bus/sys/login"
    credentials = {
        "username": "stpass",
        "password": "Qf/CNC65IVixE6kaY3v9nQ=="
    }
    
    try:
        response = requests.post(login_url, json=credentials, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != '0':
            raise ValueError(f"登录失败: {data.get('msg')}")
            
        API_TOKEN = data['data']['token']
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"登录请求失败: {str(e)}")
        return False
    except ValueError as e:
        print(str(e))
        return False
    except KeyError:
        print("响应数据格式异常，令牌获取失败")
        return False

@mcp.tool()
def getCount() -> Tuple[int, int]:
    """获取血站用户总数和被锁定的用户总数
    通过HTTP API获取数据并统计结果
    
    Returns:
        Tuple[int, int]: (总用户数, 被锁定用户数)
    """
    url = "http://imes.dev.uplasm.com/rfid/api/dic/operators?type=User"
    
    # 先执行登录认证
    if not handle_login():
        print("无法获取有效API令牌，操作终止")
        return 0, 0
    
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data["code"] != "0":
            raise ValueError(f"API返回错误码: {data['code']}")
            
        users = data.get("datas", [])
        
        total = len(users)
        locked = sum(1 for user in users if user.get("locked", False))
        
        # 打印格式化结果
        print(f"\n用户统计结果：")
        print(f"总用户数: {total}")
        print(f"被锁定用户: {locked}")
        print("-" * 30)
        
        return total, locked
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
        return 0, 0
    except ValueError as e:
        print(f"数据解析错误: {str(e)}")
        return 0, 0

def test():
    print(getCount())

if __name__ == "__main__":
    mcp.run(transport='stdio')
    #test()

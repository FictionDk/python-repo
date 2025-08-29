import requests
import json

def test_call_tool():
    url = "http://localhost:8080/mcp/message?sessionID=f12f8382-b540-4c83-8c80-68528b487566"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer sk-Q^h1rJCna17Y9xeH"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "xxx",
        "method": "callTool",
        "params": {
            "tool": "get_project",
            "arguments": {
                "uuid": "11fa3ed3-d254-41eb-bea3-4f527ca304a0"
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

if __name__ == "__main__":
    test_call_tool()

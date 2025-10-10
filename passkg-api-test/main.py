import requests
import workspace
import document
import auth
import file
import chat

model_config = [
    {
        "task": "Reasoning",
        "model": "Qwen3-235B-A22B-Instruct-2507-FP8"
    },
    {
        "task": "ImageToText",
        "model": "Qwen/Qwen2.5-VL-7B-Instruct"
    },
    {
        "task": "Audio2Text",
        "model": "Qwen/Qwen2.5-VL-7B-Instruct"
    },
    {
        "task": "Extraction",
        "model": "Qwen3-235B-A22B-Instruct-2507-FP8"
    },
    {
        "task": "Embedding",
        "model": "bge-m3"
    },
    {
        "task": "Reranking",
        "model": "bge-m3"
    }
]

def get_all_models(jwt, base_url="http://localhost:8080"):
    """
    获取所有已配置的模型信息。
    参数:
        base_url (str): API 基地址
    返回:
        list[dict] 或 None: 模型配置列表，失败返回 None
    """
    url = f"{base_url}/modelconfigs"
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + jwt})
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 成功获取 {len(models)} 个模型配置")
            return models
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络请求出错: {e}")
        return None

if __name__ == "__main__":
    jwt = auth.login("admin","stpass",base_url='http://192.168.120.246:31549')
    # r = file.upload_image_to_workspace("serwos","xiongpian.jpg",jwt=jwt)
    # print(r)
    # 测试 chat_stream 功能
    print("\n" + "="*50)
    print("🧪 正在测试 chat_stream 流式请求...")
    print("="*50)
    messages = chat.interactive_chat(workspace_id="7mofeb", jwt=jwt)
    chat.push(workspace_id="7mofeb",messages=messages, jwt=jwt)
    r_list = chat.get_logs("7mofeb",jwt=jwt)
    print(f"r={r_list}")
    # members = workspace.get_workspace_members("serwos",jwt)
    # for m in members:
    #     print(m)

    # r = workspace.retrieve_naive("血液制备","serwos",jwt)
    # print(r)

    #users = auth.list_users(jwt)
    #for u in users:
    #    print(f"{u}")
    
    #models = get_all_models(jwt)
    #if models:
        # for model in models:
        #     print(f"名称: {model['name']}")
        #     print(f"模型名: {model['modelName']}")
        #     print(f"提供商: {model['provider']}")
        #     print(f"能力: {model.get('abilities', [])}")
        #     print("-" * 40)
    # ws = workspace.create_workspace(
    #     name="HealthRegulation",
    #     description="Health and medical industry laws and regulation / 0917"
    # )
    # if ws:
    #     print("创建的 workspace:", ws)
    # workspace.set_workspace_model_config("mtlrtq", model_config)
    #print(workspace.get_workspace_model_config("mtlrtq"))
    #print(document.create_document_in_workspace("mtlrtq","test","test.md"))
    #print(document.process_document("5a6e2a28-31d2-43e1-b5fb-858af95c4031"))

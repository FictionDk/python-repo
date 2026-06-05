import requests, os
import json
from dotenv import load_dotenv

load_dotenv()

API_PATH = f"{os.getenv('MODEL_ENDPOINT')}/chat/completions"
API_KEY = os.getenv('MODEL_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')

MUSIC_INFER_PROMPT = '''
你是一个音乐曲库专家,熟知所有音乐内容、制作人、曲风等关键信息
我会提供一句简短信息,里面包含了歌曲名称
请根据信息推断歌曲的名称,并根据歌曲名称进一步获取歌手或艺术家、所属专辑、发行日期

输入样例: 未知歌手 - 04.忍者
输出样例: {'title': '忍者', 'artist': '周杰伦', 'album': '范特西', 'data':'2001'}

注意: 输出内容除了Json中需要的内容不要任何额外内容
'''

def music_infer(content: str) -> dict:
    r = __fetch(MUSIC_INFER_PROMPT, content)
    return json.loads(r)

def __fetch(prompt: str, content: str) -> str:
    if not API_KEY or not API_PATH or not MODEL_NAME:
        raise ValueError("Missing required llm environment variable")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    resp = requests.post(API_PATH, headers=headers, json={
        'model': MODEL_NAME,
        'messages': [
            {
                'role': 'system',
                'content': prompt
            },
            {
                'role': 'user',
                'content': content
            }
        ],
        'temperature': 0,
        "stream": "false"
    })
    return json.loads(resp.text)['choices'][0]['message']['content']

def test():
    #print(music_infer("Acoustic Radio - 다시 사랑한다면"))
    print(music_infer("水之畔(feat. 陶心瑶)"))

#test()
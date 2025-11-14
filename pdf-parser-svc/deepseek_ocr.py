import requests
import os

from dotenv import load_dotenv
load_dotenv()

API_PATH = os.getenv('DEEPSEEK_OCR_API_PATH')

def fetch_markdown(bytes: bytes) -> str:
    r =  __fetch(bytes, {
        'prompt_type': 'document',
        'grounding': True
    })
    return __clean(r)

def fetch_des(bytes: bytes) -> str:
    return __fetch(bytes, {
        'prompt_type': 'describe',
        'grounding': False
    })

def __clean(doc: str) -> str:
    '''
    数据清理，需要将下述格式数据中描述语句剔除，独立行的`title`、`text`、`table_caption`、`table`
    '''
    lines = doc.strip().split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line != '' and line not in ['title', 'text', 'table_caption', 'table', 'sub_title']:
            result.append(line)
        i += 1
    return '\n'.join(result)

def __fetch(bytes: bytes, data: dict) -> str:
    response = requests.post(API_PATH, files={'file': ('image.png', bytes, 'image/png')}, data=data)
    response.raise_for_status()
    result : dict = response.json()
    if result.get("success") is True:
        return result.get("text", "")
    else:
        raise ValueError(f"API request failed: {result.get('message', 'Unknown error')}")

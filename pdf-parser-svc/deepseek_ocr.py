import requests
import os

from dotenv import load_dotenv
load_dotenv()

API_PATH = os.getenv('DEEPSEEK_OCR_API_PATH')

def fetch_markdown(bytes: bytes) -> str:
    return __fetch(bytes, {
        'prompt_type': 'document',
        'grounding': True
    })

def fetch_des(bytes: bytes) -> str:
    return __fetch(bytes, {
        'prompt_type': 'describe',
        'grounding': False
    })

def __fetch(bytes: bytes, data: dict) -> str:
    response = requests.post(API_PATH, files={'file': ('image.png', bytes, 'image/png')}, data=data)
    response.raise_for_status()
    result : dict = response.json()
    if result.get("success") is True:
        return result.get("text", "")
    else:
        raise ValueError(f"API request failed: {result.get('message', 'Unknown error')}")

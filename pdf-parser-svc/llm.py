import requests
import json
import os
import base64
from deepseek_ocr import fetch_markdown
from io import BytesIO
from PIL import Image

from dotenv import load_dotenv
load_dotenv()

API_PATH = f"{os.getenv('REASONMODAL_API_PATH')}/chat/completions"
API_KEY = os.getenv('REASONMODAL_API_KEY')
MODEL_NAME = os.getenv('REASONMODAL_NAME')
if not API_KEY:
    raise ValueError("Missing required environment variable: API_KEY")

md_format_prompt = '''
你是一个专业的文档转换助手，负责将 PDF 的原始排版信息转换为结构清晰的 Markdown。
我会提供以下信息：
- 按从上到下的顺序排列的文本行，包含字体大小、是否加粗、内容
- 提取的表格内容
请根据这些信息：
1. 推断标题层级（#、##、###）
2. 识别正文、列表、代码块、引用等
3. 将表格转换为 Markdown 表格,如果有合并单元格则使用 **HTML 表格代码**，并嵌入 Markdown 中
4. 忽略页眉页脚、页码、重复标题
5. 输出完整、可读性强的 Markdown
注意：
- 不要添加额外解释，只输出 Markdown
- 保持原始语义不变
- 合理使用列表、分隔线、强调等语法

输入样例
type: text/table
top: 距离顶部的高度
text: 文本内容
data: 表格内容,使用二维数组表达
cell: 表格样式(存在合并单元格,注意data中存在的None)
bbox: 边框坐标

{'type': 'text', 'text': '11.4.2宜选用以0.9％氯化钠溶液悬浮的洗涤红细胞。不宜选用以红细胞保存 液悬浮的红细胞。', 'top': 122.27020000000005}
{'type': 'table', 'data': [['血液成分', '输注剂量', '血液检测指标改善预期', None], [None, None, '检测项目', '增加值'], ['红细胞', '10 mL/kg～15 mL/kg', 'Hb', '20 g/L～30 g/L'], ['单采血小板', '5 mL/kg～10 mL/kg', 'PLT', '30×109/L～50×109/L'], ['浓缩血小板', '2 U/10kg（患儿≥10kg）', None, None], ['a 本表给出的输注剂量和血液检测指标改善预期不适用于为紧急抢救 、大出血、新生儿换血和接受ECMO治疗的患\n儿提供输血治疗等情况。', None, None, None]], 'cell': [(70.85, 442.93, 170.15, 473.83), (70.85, 473.83, 170.15, 496.04), (70.85, 496.04, 170.15, 514.09), (70.85, 514.09, 170.15, 534.78), (70.85, 534.78, 538.65, 565.28), (170.15, 442.93, 340.25, 473.83), (170.15, 473.83, 340.25, 496.04), (170.15, 496.04, 340.25, 514.09), (170.15, 514.09, 340.25, 534.78), (340.25, 442.93, 538.65, 455.39), (340.25, 455.39, 439.45, 473.83), (340.25, 473.83, 439.45, 496.04), (340.25, 496.04, 439.45, 534.78), (439.45, 455.39, 538.65, 473.83), (439.45, 473.83, 538.65, 496.04), (439.45, 496.04, 538.65, 534.78)], 'top': 442.93, 'bottom': 565.28, 'bbox': (70.85, 442.93, 538.65, 565.28)}
"""
'''

image_format_prompt = '''
你是一个专业的文档转换助手，负责将 PDF 的原始排版信息转换为结构清晰的 Markdown。
我会提供以下信息：
- 按从上到下的顺序排列的文本行，包含字体大小、是否加粗、内容
- 提取的表格内容
请根据这些信息：
1. 推断标题层级（#、##、###）
2. 识别正文、列表、代码块、引用等
3. 将表格转换为 Markdown 表格,如果有合并单元格则使用 **HTML 表格代码**，并嵌入 Markdown 中
4. 忽略页眉页脚、页码、重复标题
5. 输出完整、可读性强的 Markdown
注意：
- 不要添加额外解释，只输出 Markdown
- 保持原始语义不变
- 合理使用列表、分隔线、强调等语法
'''

def fetch(prompt: str, content: str) -> str:
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
        "stream": "false",
    })
    # 检查响应状态码
    if resp.status_code != 200:
        raise Exception(f"API request failed with status {resp.status_code}: {resp.text}, Path: {API_PATH}")
    try:
        resp_json = resp.json()
        return resp_json['choices'][0]['message']['content']
    except KeyError as e:
        raise Exception(f"Unexpected response structure, raw value: {resp.text}: missing key {e}") from e
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse response as JSON: {resp.text}") from e

def md_format(elements: list) -> str:
    return fetch(md_format_prompt, json.dumps(elements))

def md_format_from_image(images: list[Image.Image]) -> str:
    """
    使用多模态API将图像列表转换为Markdown。根据环境变量 MULTIMODAL_STREAMING 决定使用流式或非流式模式。
    :param images: PIL图像对象列表
    :return: Markdown字符串
    """
    OCR_PATH = os.getenv('DEEPSEEK_OCR_API_PATH')
    if OCR_PATH:
        full_markdown = ""
        for _, image in enumerate(images):
            # 将PIL图像转换为Base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            page_markdown = fetch_markdown(buffered.getvalue())
            full_markdown += page_markdown + "\n"
        return full_markdown

    # 从环境变量加载多模态API配置
    API_PATH = os.getenv('MULTIMODAL_API_PATH')
    MODEL_NAME = os.getenv('MULTIMODAL_MODEL_NAME')
    API_KEY = os.getenv('MULTIMODAL_API_KEY')

    # 从环境变量加载流式配置，取默认值为 false
    STREAMING = os.getenv('MULTIMODAL_STREAMING', 'false').lower() == 'true'

    # 检查关键配置是否缺失
    if not API_PATH or not MODEL_NAME:
        raise ValueError("Missing required environment variable: MULTIMODAL_API_PATH or MODEL_NAME")

    return _md_format_from_image(images, API_PATH, API_KEY, MODEL_NAME, STREAMING, _process_streaming_response)

def _process_streaming_response(resp) -> str:
    """
    处理流式API响应。
    :param resp: requests.Response 对象
    :return: 从流中提取的Markdown字符串
    """
    page_markdown = ""
    if resp.status_code == 200:
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data:"):
                    data_str = line_str[5:].strip() # 去除 "data:" 前缀
                    if data_str == "[DONE]":
                        break # 流结束
                    try:
                        data = json.loads(data_str)
                        content = data['choices'][0]['delta'].get('content', '')
                        page_markdown += content
                    except json.JSONDecodeError:
                        continue # 跳过无法解析的行
    else:
        page_markdown = f"<!-- 无法处理图像，错误: {resp.status_code} {resp.text} -->"
    return page_markdown

def _md_format_from_image(images: list, path: str, key: str, name: str, is_stream: bool, process_response_func) -> str:
    """
    使用多模态API将图像列表转换为Markdown的通用方法。
    :param images: PIL图像对象列表
    :param path: API路径
    :param key: API密钥
    :param name: 模型名称
    :param process_response_func: 处理API响应的函数
    :return: Markdown字符串
    """
    full_markdown = ""
    for _, image in enumerate(images):
        # 将PIL图像转换为Base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        img_url = f"data:image/jpeg;base64,{img_str}"

        # 构建请求体
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {key}'
        }
        # 在通用方法中，payload的stream字段由调用者决定
        payload = {
            "model": name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": image_format_prompt},
                        {"type": "image_url", "image_url": {"url": img_url}}
                    ]
                }
            ],
            "temperature": 0,
            "stream": is_stream,
        }

        # 调用API
        resp = requests.post(path, headers=headers, json=payload)
        page_markdown = process_response_func(resp)
        full_markdown += page_markdown + "\n\n"

    return full_markdown.strip()
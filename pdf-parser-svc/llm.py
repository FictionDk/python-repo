import requests
import json
import os

from dotenv import load_dotenv
load_dotenv()

API_PATH = 'http://192.168.120.246:31825/v1/chat/completions'
API_KEY = os.getenv('API_KEY')
MODEL_NAME = 'Qwen/Qwen3-235B-A22B-Instruct-2507-FP8'

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
    return json.loads(resp.text)['choices'][0]['message']['content']

def md_format(elements: list) -> str:
    return fetch(md_format_prompt, json.dumps(elements))

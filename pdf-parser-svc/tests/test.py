
import sys
sys.path.append('..')

import requests
import os
import re
import llm
import deepseek_ocr as ocr
import json

from PIL import Image
import io

# 定义服务地址和端口
# url = 'http://127.0.0.1:8188/convert'
url = 'http://192.168.141.203:8188/convert'
# url = 'http://192.168.120.246:30191/convert'
test_file_path = 'D:\\Doc\\download\\《血站技术操作规程（2019版）》.pdf'

def save_markdown_to_file(markdown_content):
    """将Markdown内容以标题作为文件名保存到本地"""
    # 提取第一个##标题作为文件名
    title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    if title_match:
        # 获取标题文本
        title = title_match.group(1).strip()
        # 清理文件名中的非法字符
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', title)
    else:
        # 如果没有找到标题，使用默认文件名
        filename = 'output'
    
    # 添加.md扩展名
    filename += '.md'
    
    # 保存文件到当前工作目录
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"\nMarkdown内容已保存到文件：{filename}")
    except Exception as e:
        print(f"保存文件时发生错误：{e}")

def test_post(pdf_file_path = 'req_t.pdf', direct_ocr = 'false'):
    # 检查文件是否存在
    if not os.path.exists(pdf_file_path):
        print(f"错误：文件 {pdf_file_path} 不存在。")
    else:
        # 以二进制模式打开PDF文件
        with open(pdf_file_path, 'rb') as pdf_file:
            # 构造文件上传的字典
            files = {'pdf': pdf_file}
            rel_url = f"{url}?direct_ocr={direct_ocr}"
            print(f"url={rel_url}")
            try:
                # 发送POST请求到Flask服务
                response = requests.post(rel_url, files=files)
                # 检查响应状态码
                if response.status_code == 200:
                    # 解析返回的JSON数据
                    result = response.json()
                    markdown_content = result.get('markdown', '')
                    
                    # 打印解析后的Markdown内容
                    #print("解析后的Markdown内容：\n")
                    #print(markdown_content)
                    
                    # 调用保存方法
                    save_markdown_to_file(markdown_content)
                else:
                    print(f"请求失败，状态码：{response.status_code}")
                    print("响应内容：", response.text)
                    
            except requests.exceptions.RequestException as e:
                print(f"请求过程中发生错误：{e}")

def process_local_image(image_path: str) -> str:
    """
    读取本地图片文件并将其转换为Markdown格式。
    :param image_path: 本地图片文件路径
    :return: 转换后的Markdown字符串
    """
    from PIL import Image
    
    # 打开本地图片文件
    with Image.open(image_path) as img:
        # 将图片转换为RGB模式（如果需要）
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        # 调用md_format_from_image方法处理图片
        return llm.md_format_from_image([img])

def test_llm():
    r = process_local_image('20251013_1.png')
    print(r)

def test_ocr_fetch(is_des=False):
    """测试 fetch_markdown 方法，使用PIL读取并预览指定图片，然后转换为 Markdown"""
    image_path = "微信截图_20251106145127.png"
    if is_des:
        image_path = '微信截图_20251106151615.png'
    if not os.path.exists(image_path):
        print(f"错误：图片文件 {image_path} 不存在。")
        return
    
    # 使用PIL打开并预览图片
    with Image.open(image_path) as img:
        img.show()  # 这会调用系统默认的图片查看器预览图片
        
        # 将PIL图像对象转换为字节流
        byte_stream = io.BytesIO()
        img.save(byte_stream, format='PNG')  # 保存为PNG格式到内存中的字节流
        image_bytes = byte_stream.getvalue()  # 获取字节流内容

    if is_des:
        r = ocr.fetch_des(image_bytes)
    else:
        r = ocr.fetch_markdown(image_bytes)
    print(f"result={r}")

def test_llm_fetch():
    """测试 llm.md_format 方法，使用模拟的排版元素数据生成 Markdown"""
    # 构造模拟的排版元素数据
    mock_elements = [
        {
            "type": "text",
            "top": 100.0,
            "text": "这是一个测试标题",
            "font_size": 16,
            "bold": True
        },
        {
            "type": "text",
            "top": 150.0,
            "text": "这是一段普通的正文文本，用于测试。",
            "font_size": 12,
            "bold": False
        },
        {
            "type": "table",
            "top": 200.0,
            "data": [
                ["姓名", "年龄", "城市"],
                ["张三", "25", "北京"],
                ["李四", "30", "上海"]
            ],
            "cell": [
                (50, 200, 150, 230), (150, 200, 250, 230), (250, 200, 350, 230),
                (50, 230, 150, 260), (150, 230, 250, 260), (250, 230, 350, 260),
                (50, 260, 150, 290), (150, 260, 250, 290), (250, 260, 350, 290)
            ],
            "bbox": (50, 200, 350, 290)
        },
        {
            "type": "text",
            "top": 300.0,
            "text": "表格之后的另一段文本。",
            "font_size": 12,
            "bold": False
        }
    ]
    
    # 调用 llm.md_format 方法
    result_markdown = llm.md_format(mock_elements)
    
    # 打印结果
    print("生成的Markdown内容：\n")
    print(result_markdown)

def test_convert_stream(pdf_file_path='req_t.pdf'):
    """测试 /convert_stream 接口，验证SSE流式响应"""
    # 检查文件是否存在
    if not os.path.exists(pdf_file_path):
        print(f"错误：文件 {pdf_file_path} 不存在。")
        return
    # 以二进制模式打开PDF文件
    with open(pdf_file_path, 'rb') as pdf_file:
        # 构造文件上传的字典
        files = {'pdf': pdf_file}
        try:
            # 发送POST请求到Flask服务，启用流式响应
            loc_url = str(url).replace('convert','convert_stream')
            print(loc_url)
            response = requests.post(loc_url, files=files, stream=True)
            # 检查响应状态码
            if response.status_code == 200:
                print("开始接收流式响应...")
                received_events = []
                # 逐行处理SSE响应
                for line in response.iter_lines():
                    if line:  # 过滤空行
                        line_str = line.decode('utf-8')
                        print(f"接收到: {line_str}")
                        if line_str.startswith('data:'):
                            # 解析JSON数据
                            try:
                                data = json.loads(line_str[5:].strip())  # 去掉'data:'前缀
                                received_events.append(data)

                                # 简单验证进度
                                if data.get('progress') == 10 and data.get('message') == '文件已接收并保存':
                                    print("✓ 收到初始进度事件")
                                elif data.get('progress') == 100 and data.get('message') == '转换完成':
                                    print("✓ 收到完成进度事件")
                                    # 提取并保存Markdown内容
                                    markdown_content = data.get('markdown', '')
                                    if markdown_content:
                                        save_markdown_to_file(markdown_content)
                                    break
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {e}")
                                continue
                print(f"共接收 {len(received_events)} 个事件")
            else:
                print(f"请求失败，状态码：{response.status_code}")
                print("响应内容：", response.text)
        except requests.exceptions.RequestException as e:
            print(f"请求过程中发生错误：{e}")

def process_md_file(file_path: str):
    """
    读取指定的 .md 文件，调用 __clean 方法处理内容，并覆盖原文件
    :param file_path: .md 文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在。")
        return
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 调用 __clean 方法处理内容
    cleaned_content = ocr.__clean(content)
    
    # 将处理后的内容写回原文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"文件 {file_path} 已成功处理并覆盖原内容。")

# 《血站技术操作规程（2019版）》.pdf 单采血浆站技术操作规程(2022 年版).pdf
#test_llm_fetch()
#test_ocr_fetch(True)
test_post('D:\\Doc\\2025年四季度\\山东省医疗机构样本外送检测管理规范.pdf','true')
#test_convert_stream('D:\\Doc\\download\\NPF.pdf')
#test_convert_stream('D:\\Doc\\download\\《血站技术操作规程（2019版）》.pdf')
#test_convert_stream()
# 调用新功能处理 xxxx.md 文件
#process_md_file('血站技术操作规程.md')

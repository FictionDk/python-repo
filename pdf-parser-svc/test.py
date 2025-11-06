import requests
import os
import re
import llm
import deepseek_ocr as ocr

from PIL import Image
import io

# 定义服务地址和端口
url = 'http://localhost:8188/convert'
# url = 'http://192.168.120.246:30191/convert'

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

def test_post():
    # 指定要上传的本地PDF文件路径
    pdf_file_path = 'req_t.pdf'
    # 检查文件是否存在
    if not os.path.exists(pdf_file_path):
        print(f"错误：文件 {pdf_file_path} 不存在。")
    else:
        # 以二进制模式打开PDF文件
        with open(pdf_file_path, 'rb') as pdf_file:
            # 构造文件上传的字典
            files = {'pdf': pdf_file}
            
            try:
                # 发送POST请求到Flask服务
                response = requests.post(url, files=files)
                
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

test_ocr_fetch(True)

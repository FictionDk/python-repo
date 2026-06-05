from pathlib import Path
import requests
import os
import re

url = 'http://192.168.120.246:30191/convert'

def test_post(pdf_file_path = 'req_t.pdf', direct_ocr = 'true'):
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

def process_files_in_directory(directory_path):
    """
    Read all files from the specified directory and call test_post method for each file.
    
    Args:
        directory_path (str): Path to the directory containing files to process
    """
    # Convert to Path object for easier handling
    dir_path = Path(directory_path)
    
    # Check if directory exists
    if not dir_path.exists():
        print(f"Error: Directory {directory_path} does not exist.")
        return
    
    # Check if path is a directory
    if not dir_path.is_dir():
        print(f"Error: {directory_path} is not a directory.")
        return
    
    # Get all files in the directory (non-recursive)
    files = [f for f in dir_path.iterdir() if f.is_file()]
    
    if not files:
        print(f"No files found in directory: {directory_path}")
        return
    
    print(f"Found {len(files)} files in {directory_path}. Starting processing...")
    
    # Process each file
    for file_path in files:
        print(f"\nProcessing file: {file_path}")
        try:
            # Call test_post method with the file path
            test_post(pdf_file_path=str(file_path), direct_ocr='false')
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    
    print("\nProcessing completed.")

if __name__ == "__main__":
    # Specify the target directory
    target_directory = r"D:\Doc\2025年四季度\file"
    
    # Process all files in the directory
    process_files_in_directory(target_directory)

import pdfplumber
from pdfplumber.page import Page
from pdf2image import convert_from_path
from PIL import Image

def get_elements(pdf_path):
    eles = []
    with pdfplumber.open(pdf_path) as pdf:
        for _, page in enumerate(pdf.pages):
            p = merge_text_and_tables(page)
            eles.append(p)
    return eles

def extract_images_from_pdf(pdf_path, dpi=200) -> list[Image.Image]:
    """
    将PDF的每一页转换为图像。
    :param pdf_path: PDF文件路径
    :param dpi: 图像分辨率
    :return: PIL图像对象列表
    """
    images = convert_from_path(pdf_path, dpi=dpi)
    return images

def merge_text_and_tables(page):
    lines = extract_lines_with_position(page)
    tables = extract_tables_with_position(page)
    # 合并所有元素
    elements = lines + tables
    # 按 top 从上到下排序（PDF 坐标系：top 越大越靠上）
    elements.sort(key=lambda x: x["top"], reverse=False)  # 从上到下
    return elements

def extract_lines_with_position(page: Page):
    """提取每行文本及其垂直位置（top）"""
    lines = []
    current_para = []
    last_top = None
    tolerance = 18  # 行间距容差
    for char in page.chars:
        if not current_para:
            current_para.append(char)
            last_top = char["top"]
        else:
            # 如果当前字符的 top 与上一行差距较大，视为新段
            if abs(char["top"] - last_top) > tolerance:
                text = "".join(c["text"] for c in current_para)
                if text == "":
                    continue
                lines.append({
                    "type": "text",
                    "text": text.strip(),
                    "top": last_top,
                })
                current_para = [char]
                last_top = char["top"]
            else:
                current_para.append(char)

    # 添加最后一段
    if current_para:
        text = "".join(c["text"] for c in current_para)
        lines.append({
            "type": "text",
            "text": text.strip(),
            "top": last_top,
        })
    return lines

def extract_tables_with_position(page:Page):
    """提取表格及其位置（使用 bbox 的 top）"""
    tables = []
    table_data = page.extract_tables()  # 提取表格内容
    table_bboxes = page.find_tables()  # 提取表格边界框
    for _, (table, bbox) in enumerate(zip(table_data, table_bboxes)):
        tables.append({
            "type": "table",
            "data": table,
            "cell": bbox.cells,
            "top": bbox.bbox[1],  # 表格顶部 y 坐标 (top is at index 1)
            "bottom": bbox.bbox[3],  # 表格底部 y 坐标 (bottom is at index 3)
            "bbox": bbox.bbox,  # 使用 bbox 元组 (left, top, right, bottom)
        })
    return tables

# def tests():
#     obj_arr = get_elements('D:\\Doc\\download\\《血站技术操作规程（2019版）》.pdf')
#     size = 0
#     print("========================================================================")
#     for obj in obj_arr:
#         print(obj)
#         size += len(obj)
#         for o in obj:
#             print(o)
#     print(f"len={len(obj_arr)},size={size}")

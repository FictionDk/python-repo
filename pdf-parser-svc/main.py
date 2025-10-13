import pdf
import llm
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    pdf_file = request.files['pdf']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_filename = f"temp_{timestamp}.pdf"

    try:
        pdf_file.save(temp_filename)
        
        try:
            # 首先尝试用文本提取方法
            elements = pdf.get_elements(temp_filename)
            # 将所有页面的元素列表合并为一个大的元素列表（扁平化）
            all_elements = [element for page_elements in elements for element in page_elements]
            # 然后从这个大的列表中提取文本
            text_content = " ".join([e["text"] for e in all_elements if e.get("type") == "text"])
            if len(text_content.strip()) < 10:
                # 判定为扫描件，使用多模态模型
                images = pdf.extract_images_from_pdf(temp_filename)
                result = llm.md_format_from_image(images)
            else:
                # 正常文本PDF，使用原有方法
                result = llm.md_format(elements)
            return jsonify({"markdown": result})
        except Exception as e:
            logging.exception(f"An error occurred during PDF processing: {e}")
            return jsonify({"error": f"Internal server error: {e}"}), 500
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8188)

import pdf
import llm
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import logging
import json

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

@app.route('/convert_stream', methods=['POST'])
def convert_stream():
    logging.info("start streaming")
    def generate():
        yield f"data: {json.dumps({'status': 'success', 'message': '文件开始保存', 'progress': 0})}\n\n"
        pdf_file = request.files['pdf']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_filename = f"temp_{timestamp}.pdf"
        try:
            pdf_file.save(temp_filename)
            yield f"data: {json.dumps({'status': 'success', 'message': '文件已接收并保存', 'progress': 10})}\n\n"
            direct_ocr = request.args.get('direct_ocr', 'false').lower() == 'true'
            if direct_ocr:
                result = process_ocr(temp_filename)
            else:
                result = process_llm(temp_filename)
            yield f"data: {json.dumps({'status': 'success', 'message': '转换完成', 'progress': 100, 'markdown': result})}\n\n"
        except Exception as e:
            logging.exception(f"An error occurred during PDF processing: {e}")
            yield f"data: {json.dumps({'status': 'error', 'message': f'Internal server error: {e}'})}\n\n"
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/convert', methods=['POST'])
def convert():
    pdf_file = request.files['pdf']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_filename = f"temp_{timestamp}.pdf"
    try:
        pdf_file.save(temp_filename)
        try:
            direct_ocr = request.args.get('direct_ocr', 'false').lower() == 'true'
            if direct_ocr:
                result = process_ocr(temp_filename)
            else:
                result = process_llm(temp_filename)
            return jsonify({"markdown": result})
        except Exception as e:
            logging.exception(f"An error occurred during PDF processing: {e}")
            return jsonify({"error": f"Internal server error: {e}"}), 500
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def process_ocr(path_name: str) -> str:
    logging.info("start get images by pdf")
    images = pdf.extract_images_from_pdf(path_name)
    logging.info(f"get {len(images)} from pdf, starting ocr")
    return llm.md_format_from_image(images)

def process_llm(path_name: str) -> str:
    logging.info("start get elements by pdf")
    elements = pdf.get_elements(path_name)
    all_elements = [element for page_elements in elements for element in page_elements]
    logging.info(f"get {len(all_elements)} from pdf")
    text_content = " ".join([e["text"] for e in all_elements if e.get("type") == "text"])
    if len(text_content.strip()) < 10:
        return process_ocr(path_name)
    else:
        logging.info(f"start llm for elements")
        return llm.md_format(all_elements)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8188)

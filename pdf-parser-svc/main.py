import pdf
import llm
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    pdf_file = request.files['pdf']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_filename = f"temp_{timestamp}.pdf"

    try:
        pdf_file.save(temp_filename)
        elements = pdf.get_elements(temp_filename)
        result = llm.md_format(elements)
        return jsonify({"markdown": result})
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8188)

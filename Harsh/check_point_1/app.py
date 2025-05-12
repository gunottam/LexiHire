from flask import Flask, request, jsonify
import os
import fitz  # PyMuPDF
import docx
from flask_cors import CORS
import json
from tokenizer import ResumeTokenizer
from parser_service import ResumeParser

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_text(file_path):
    # Function to extract text from PDF or Word file
    text = ''
    if file_path.endswith('.pdf'):
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text
    return text

@app.route('/process', methods=['POST'])
def process_text():
    folder_path = "C:/Users/ashmi/Desktop/Lexihire/ashmit/check_point_1/outputs"

    # Create a list to store results
    processed_files = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

            print(f"Processing {filename}...")

            with open(file_path, 'r', encoding='utf-8') as file:
                resume_text = file.read()

            tokenizer = ResumeTokenizer(resume_text)
            tokens = tokenizer.tokenize()

            parser = ResumeParser(tokens)
            symbol_table = parser.parse()

            modified_content = json.dumps(symbol_table, indent=4)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)

            processed_files.append({
                'filename': filename,
                'status': 'processed'
            })

            print(f"Done processing {filename} ✅\n")
    
    # Return a success response with processed files
    return jsonify({"status": "success", "processed_files": processed_files})


@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')  # Allow multiple file uploads
    response_data = []

    for file in files:
        if file:
            filename = file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # Extract text without tokenization
            text = extract_text(save_path)

            # Save plain text into a separate output file
            output_filename = f"text_{os.path.splitext(filename)[0]}.txt"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)

            response_data.append({
                'filename': filename,
                'text_output': output_filename
            })

    return jsonify({"status": "success", "data": response_data})

if __name__ == '__main__':
    app.run(debug=True)

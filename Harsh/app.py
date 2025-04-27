from flask import Flask, request, render_template
import os
import fitz  # PyMuPDF
import docx

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to extract text from files
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text.strip()
    
    elif ext == '.docx':
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()

    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    else:
        return ""

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')  # Allow multiple file uploads

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

    return 'All files processed and saved successfully!'

if __name__ == '__main__':
    app.run(debug=True)

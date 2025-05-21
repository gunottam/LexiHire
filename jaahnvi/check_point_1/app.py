from flask import Flask, request, jsonify
from flask import send_file
import zipfile
import spacy
nlp = spacy.load("en_core_web_sm")
import os
import fitz  
import docx
from flask_cors import CORS
import json
from tokenizer import ResumeTokenizer
from parser_service import ResumeParser
from keyword_generator import generate_keywords  

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clear_previous_uploads():
    for file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    for file in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    job_role_path = "current_job_role.txt"
    if os.path.exists(job_role_path):
        os.remove(job_role_path)



# ============================== #
# TEXT EXTRACTION LOGIC
# ============================== #
def extract_text(file_path):
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

def clean_text(text):
    doc = nlp(text)
    return ' '.join([
        token.lemma_ for token in doc
        if not token.is_stop and token.is_alpha
    ])
# ============================== #
# ROUTE: UPLOAD
# ============================== #
@app.route('/upload', methods=['POST'])
def upload_files():
    clear_previous_uploads()
    
    files = request.files.getlist('files')
    job_role = request.form.get('jobRole', '').strip()
    response_data = []

    # Save job role to a temp file
    with open("current_job_role.txt", "w", encoding="utf-8") as f:
        f.write(job_role)

    for file in files:
        if file:
            filename = file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            text = extract_text(save_path)
            output_filename = f"{os.path.splitext(filename)[0]}.txt"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)

            response_data.append({
                'filename': filename,
                'text_output': output_filename
            })

    return jsonify({"status": "success", "data": response_data})

# ============================== #
# ROUTE: PROCESS (parse resumes)
# ============================== #
@app.route('/process', methods=['POST'])
def process_text():
    folder_path = OUTPUT_FOLDER
    processed_files = []

    # Read job role from file
    try:
        with open("current_job_role.txt", "r", encoding="utf-8") as f:
            job_role = f.read().strip()
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Job role not specified."}), 400

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

            for key, value in symbol_table.items():
                if isinstance(value, str):
                    symbol_table[key] = clean_text(value)
                elif isinstance(value, list):
                    symbol_table[key] = [clean_text(item) if isinstance(item, str) else item for item in value]

            modified_content = json.dumps(symbol_table, indent=4)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)

            processed_files.append({
                'filename': filename,
                'status': 'processed'
            })

            print(f"Done processing {filename} ✅\n")

    generate_keywords(job_role, os.path.join(OUTPUT_FOLDER, "keywords.json"))

    score_resumes()

    return jsonify({"status": "success", "processed_files": processed_files})


# ============================== #
# ROUTE: GENERATE KEYWORDS
# ============================== #
@app.route('/generate-keywords', methods=['GET'])
def generate_keywords_route():
    try:
        with open("current_job_role.txt", "r", encoding="utf-8") as f:
            job_title = f.read().strip()
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Job role not specified."}), 400

    output_path = os.path.join(OUTPUT_FOLDER, "keywords.json")
    result = generate_keywords(job_title, output_path)

    if result["status"] == "success":
        return jsonify({
            "status": "success",
            "message": f"Keywords generated for job title '{job_title}'",
            "keywords_file": "keywords.json",
            "keywords": result["keywords"]
        })
    else:
        return jsonify({
            "status": "error",
            "message": result["message"]
        }), 500

        
@app.route('/score', methods=['GET'])
def score_resumes():
    keyword_path = os.path.join(OUTPUT_FOLDER, "keywords.json")
    if not os.path.exists(keyword_path):
        return jsonify({"status": "error", "message": "keywords.json not found"}), 400

    with open(keyword_path, 'r', encoding='utf-8') as f:
        keyword_list = json.load(f)
    keyword_map = {k['keyword'].lower(): k['weight'] for k in keyword_list}
    max_possible_score = sum(keyword_map.values())

    scored_resumes = []

    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith(".txt") and filename != "keywords.json":
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                symbol_table = json.load(f)

            flat_text = json.dumps(symbol_table).lower()
            score = 0.0

            for keyword, weight in keyword_map.items():
                count = flat_text.count(keyword)
                score += count * weight

            normalized_score = round(score / max_possible_score, 4)
            scored_resumes.append({
                "filename": filename,
                "raw_score": score,
                "normalized_score": normalized_score
            })

    scored_resumes.sort(key=lambda x: x['normalized_score'], reverse=True)

    for i, resume in enumerate(scored_resumes, 1):
        old_path = os.path.join(OUTPUT_FOLDER, resume["filename"])
        new_name = f"{i:02d}_score{resume['normalized_score']}_{resume['filename']}"
        new_path = os.path.join(OUTPUT_FOLDER, new_name)
        os.rename(old_path, new_path)
        resume['ranked_filename'] = new_name

    with open(os.path.join(OUTPUT_FOLDER, "ranking.json"), 'w', encoding='utf-8') as f:
        json.dump(scored_resumes, f, indent=4)
        
    reorder_uploads_by_ranking()


    return jsonify({"status": "success", "rankings": scored_resumes})

def reorder_uploads_by_ranking():
    ranking_path = os.path.join(OUTPUT_FOLDER, "ranking.json")
    if not os.path.exists(ranking_path):
        print("❌ ranking.json not found.")
        return

    with open(ranking_path, 'r', encoding='utf-8') as f:
        ranked_resumes = json.load(f)

    upload_files = os.listdir(UPLOAD_FOLDER)

    for resume in ranked_resumes:
        original_txt_name = resume["filename"]
        original_base_name = os.path.splitext(original_txt_name)[0].lower()

        matching_file = None
        for file in upload_files:
            file_base = os.path.splitext(file)[0].lower()
            if file_base == original_base_name:
                matching_file = file
                break

        if matching_file:
            rank_prefix = resume["ranked_filename"].split("_")[0]  # e.g., "01"
            new_name = f"{rank_prefix}_{matching_file}"
            old_path = os.path.join(UPLOAD_FOLDER, matching_file)
            new_path = os.path.join(UPLOAD_FOLDER, new_name)
            os.rename(old_path, new_path)
            print(f"✅ Renamed: {matching_file} ➝ {new_name}")
        else:
            print(f"⚠️ No match found in uploads for: {original_txt_name}")


@app.route('/rankings', methods=['GET'])
def get_rankings():
    ranking_path = os.path.join(OUTPUT_FOLDER, "ranking.json")
    if not os.path.exists(ranking_path):
        return jsonify({"status": "error", "message": "No rankings found"}), 404

    with open(ranking_path, 'r', encoding='utf-8') as f:
        ranked = json.load(f)

    return jsonify({"status": "success", "rankings": ranked})

@app.route('/download-ranked-resumes', methods=['GET'])
def download_ranked_resumes():
    zip_filename = "ranked_resumes.zip"
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(UPLOAD_FOLDER):
            if file.endswith((".pdf", ".docx", ".txt")):
                full_path = os.path.join(UPLOAD_FOLDER, file)
                zipf.write(full_path, arcname=file)

    return send_file(zip_path, as_attachment=True)

# ============================== #
# RUN SERVER
# ============================== #
if __name__ == '__main__':
    app.run(debug=True)

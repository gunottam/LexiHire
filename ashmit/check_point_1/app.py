from flask import Flask, request, jsonify
import spacy
import json
import fitz
import docx
from io import BytesIO
from flask_cors import CORS
from tokenizer import ResumeTokenizer
from parser_service import ResumeParser
from keyword_generator import generate_keywords
from databas.resume_store import clear_resume_table, insert_ranked_resumes
from databas.resume_store import get_ranked_resumes
from supabase_utils.supabase_client import supabase

app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")

def extract_text(file_bytes, filename):
    text = ''
    if filename.endswith('.pdf'):
        doc = fitz.open(stream=file_bytes, filetype='pdf')
        for page in doc:
            text += page.get_text()
    elif filename.endswith('.docx'):
        buffer = BytesIO(file_bytes)
        doc = docx.Document(buffer)
        for para in doc.paragraphs:
            text += para.text
    return text

def clean_text(text):
    doc = nlp(text)
    return ' '.join([
        token.lemma_ for token in doc
        if not token.is_stop and token.is_alpha
    ])

def clear_supabase_bucket(bucket_name="resumes"):
    objects = supabase.storage.from_(bucket_name).list()
    if objects:
        supabase.storage.from_(bucket_name).remove([obj["name"] for obj in objects])

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    job_role = request.form.get('jobRole', '').strip()
    response_data = []

    if not job_role:
        return jsonify({"status": "error", "message": "Job role is required"}), 400

    # Save job role
    with open("current_job_role.txt", "w", encoding="utf-8") as f:
        f.write(job_role)

    # Clear old DB and storage
    clear_resume_table()
    clear_supabase_bucket()

    for file in files:
        filename = file.filename
        file_bytes = file.read()

        # ✅ Upload original file to 'originals/'
        supabase.storage.from_("resumes").update(
            f"originals/{filename}",
            file_bytes,
            {"content-type": file.mimetype}
        )

        # ✅ Prepare text path
        output_filename = filename.rsplit(".", 1)[0] + ".txt"
        text_path = f"text/{output_filename}"

        # ✅ Try deleting if it exists
        try:
            supabase.storage.from_("resumes").remove([text_path])
        except Exception as e:
            print(f"File may not exist yet, skipping delete: {e}")

        # ✅ Extract text from file
        text = extract_text(file_bytes, filename)

        # ✅ Upload extracted text
        supabase.storage.from_("resumes").upload(
            text_path,
            text.encode("utf-8"),
            {"content-type": "text/plain"}
        )

        # ✅ Add to response
        response_data.append({
            "filename": filename,
            "text_output": output_filename
        })

    return jsonify({"status": "success", "data": response_data})


@app.route('/process', methods=['POST'])
def process_text():
    try:
        with open("current_job_role.txt", "r", encoding="utf-8") as f:
            job_role = f.read().strip()
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Job role not specified."}), 400

    processed_files = []
    text_files = supabase.storage.from_("resumes").list("text")

    for obj in text_files:
        filename = obj["name"]
        if not filename.endswith(".txt"):
            continue

        response = supabase.storage.from_("resumes").download(f"text/{filename}")

        resume_text = response.decode("utf-8")


        tokenizer = ResumeTokenizer(resume_text)
        tokens = tokenizer.tokenize()
        parser = ResumeParser(tokens)
        symbol_table = parser.parse()

        for key, value in symbol_table.items():
            if isinstance(value, str):
                symbol_table[key] = clean_text(value)
            elif isinstance(value, list):
                symbol_table[key] = [clean_text(item) if isinstance(item, str) else item for item in value]

        processed_files.append({
            "filename": filename,
            "status": "processed",
            "symbol_table": symbol_table
        })

    keyword_list = generate_keywords(job_role)["keywords"]
    keyword_map = {k["keyword"].lower(): k["weight"] for k in keyword_list}
    max_possible_score = sum(keyword_map.values())

    ranked = []
    for item in processed_files:
        flat_text = json.dumps(item["symbol_table"]).lower()
        score = sum(flat_text.count(k) * w for k, w in keyword_map.items())
        norm_score = round(score / max_possible_score, 4)
        ranked.append({
            "filename": item["filename"],
            "raw_score": score,
            "normalized_score": norm_score
        })

    ranked.sort(key=lambda x: x["normalized_score"], reverse=True)

    clear_resume_table()
    insert_ranked_resumes(ranked, job_role)

    return jsonify({"status": "success", "rankings": ranked})

@app.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        rankings = get_ranked_resumes()
        print(f"DEBUG: Rankings fetched: {rankings}")  # Debug print

        if not rankings:
            return jsonify({"status": "error", "message": "No rankings found"}), 404

        return jsonify({"status": "success", "rankings": rankings})
    except Exception as e:
        print(f"ERROR in /rankings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)

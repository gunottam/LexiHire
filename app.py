from flask import Flask, request, jsonify
import json
import os
import time
import fitz
import docx
from io import BytesIO
import zipfile
from flask_cors import CORS
from compiler.pipeline import CompilerPipeline
from databas.resume_store import clear_resume_table, insert_ranked_resumes
from databas.resume_store import get_ranked_resumes
from supabase_utils.supabase_client import supabase

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["PROPAGATE_EXCEPTIONS"] = False

# Tracks text filenames from the last successful /upload so /process can skip
# listing the entire bucket (which is slow when many objects exist).
LAST_UPLOAD_MANIFEST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_last_upload_text_files.json"
)
_STORAGE_REMOVE_CHUNK = 100


def extract_text(file_bytes, filename):
    """Extract raw text from a PDF or DOCX file."""
    text = ''
    if filename.lower().endswith('.pdf'):
        doc = fitz.open(stream=file_bytes, filetype='pdf')
        try:
            for page in doc:
                text += page.get_text()
        finally:
            doc.close()
    elif filename.lower().endswith('.docx'):
        buffer = BytesIO(file_bytes)
        doc = docx.Document(buffer)
        for para in doc.paragraphs:
            text += para.text + '\n'
    return text


def _remove_storage_paths(paths, bucket_name="resumes"):
    """Remove specific paths only (no list). Chunked for large batches."""
    if not paths:
        return
    bucket = supabase.storage.from_(bucket_name)
    for i in range(0, len(paths), _STORAGE_REMOVE_CHUNK):
        chunk = paths[i : i + _STORAGE_REMOVE_CHUNK]
        try:
            bucket.remove(chunk)
        except Exception as e:
            print(f"  ⚠ Storage remove chunk failed: {e}")


def _read_last_upload_manifest():
    try:
        with open(LAST_UPLOAD_MANIFEST, "r", encoding="utf-8") as f:
            names = json.load(f)
        if isinstance(names, list) and all(isinstance(n, str) for n in names):
            return names
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        pass
    return None


def _write_last_upload_manifest(text_filenames):
    try:
        with open(LAST_UPLOAD_MANIFEST, "w", encoding="utf-8") as f:
            json.dump(text_filenames, f)
    except OSError as e:
        print(f"  ⚠ Could not write upload manifest: {e}")


def safe_db_clear():
    """Clear the resume table, but don't crash if DB is unreachable."""
    try:
        clear_resume_table()
    except Exception as e:
        print(f"  ⚠ DB clear failed (non-fatal): {e}")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    # Helps some browsers when the UI is on localhost and the API is on loopback.
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    print(f"UNHANDLED ERROR: {error}")
    return jsonify({"status": "error", "message": str(error)}), 500


@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        t_start = time.time()
        files = request.files.getlist('files')
        job_role = request.form.get('jobRole', '').strip()
        response_data = []

        if not job_role:
            return jsonify({"status": "error", "message": "Job role is required"}), 400

        if not files:
            return jsonify({"status": "error", "message": "No files uploaded"}), 400

        with open("current_job_role.txt", "w", encoding="utf-8") as f:
            f.write(job_role)

        print(f"\n{'='*60}")
        print(f"📤 Upload: {len(files)} file(s) for role: '{job_role}'")

        # Clear old rankings; avoid listing entire storage buckets (very slow).
        t0 = time.time()
        safe_db_clear()
        paths_to_remove = []
        for file in files:
            fn = file.filename
            if not fn:
                continue
            if not (fn.lower().endswith(".pdf") or fn.lower().endswith(".docx")):
                return jsonify({"status": "error", "message": f"Unsupported file type: {fn}"}), 400
            out_txt = fn.rsplit(".", 1)[0] + ".txt"
            paths_to_remove.append(f"originals/{fn}")
            paths_to_remove.append(f"text/{out_txt}")
        _remove_storage_paths(paths_to_remove)
        print(f"  ⏱ Cleanup (targeted remove) took {(time.time()-t0)*1000:.0f}ms")

        text_outputs_for_manifest = []

        for file in files:
            filename = file.filename
            if not filename:
                continue

            if not (filename.lower().endswith('.pdf') or filename.lower().endswith('.docx')):
                return jsonify({"status": "error", "message": f"Unsupported file type: {filename}"}), 400

            t0 = time.time()
            file_bytes = file.read()

            try:
                supabase.storage.from_("resumes").upload(
                    f"originals/{filename}",
                    file_bytes,
                    {"content-type": file.mimetype}
                )
            except Exception as e:
                print(f"  ❌ Upload failed for {filename}: {e}")
                return jsonify({"status": "error", "message": f"Upload failed for {filename}: {str(e)}"}), 500

            output_filename = filename.rsplit(".", 1)[0] + ".txt"
            text_path = f"text/{output_filename}"

            text = extract_text(file_bytes, filename)

            try:
                supabase.storage.from_("resumes").upload(
                    text_path,
                    text.encode("utf-8"),
                    {"content-type": "text/plain"}
                )
            except Exception as e:
                print(f"  ❌ Text upload failed for {text_path}: {e}")
                return jsonify({"status": "error", "message": f"Text upload failed for {filename}: {str(e)}"}), 500

            elapsed = (time.time() - t0) * 1000
            print(f"  📄 {filename} → {output_filename} ({elapsed:.0f}ms)")
            response_data.append({
                "filename": filename,
                "text_output": output_filename
            })
            text_outputs_for_manifest.append(output_filename)

        _write_last_upload_manifest(text_outputs_for_manifest)

        total = (time.time() - t_start) * 1000
        print(f"✅ Upload complete: {len(response_data)} file(s) in {total:.0f}ms")
        print(f"{'='*60}\n")

        return jsonify({"status": "success", "uploaded_count": len(response_data), "data": response_data})
    except Exception as e:
        print(f"ERROR in /upload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/process', methods=['POST'])
def process_text():
    """
    Process uploaded resumes through the compiler pipeline.
    """
    try:
        t_start = time.time()

        try:
            with open("current_job_role.txt", "r", encoding="utf-8") as f:
                job_role = f.read().strip()
        except FileNotFoundError:
            return jsonify({"status": "error", "message": "Job role not specified."}), 400

        # Prefer manifest from last /upload (avoids listing entire bucket).
        t0 = time.time()
        manifest_names = _read_last_upload_manifest()
        if manifest_names:
            text_files = [{"name": n} for n in manifest_names if n.endswith(".txt")]
            list_ms = (time.time() - t0) * 1000
            print(f"\n{'='*60}")
            print(f"⚙ Processing {len(text_files)} resume(s) for role: '{job_role}'")
            print(f"  ⏱ File list: manifest ({list_ms:.0f}ms)")
        else:
            text_files = supabase.storage.from_("resumes").list("text")
            text_files = [obj for obj in (text_files or []) if obj.get("name", "").endswith(".txt")]
            list_ms = (time.time() - t0) * 1000
            print(f"\n{'='*60}")
            print(f"⚙ Processing {len(text_files)} resume(s) for role: '{job_role}'")
            print(f"  ⏱ File listing (storage): {list_ms:.0f}ms")

        if not text_files:
            return jsonify({"status": "error", "message": "No text files found to process"}), 400

        bucket = supabase.storage.from_("resumes")

        # Sequential downloads: Supabase Python client is not guaranteed thread-safe.
        t_dl = time.time()
        downloads = {}
        for obj in text_files:
            name = obj["name"]
            raw = bucket.download(f"text/{name}")
            downloads[name] = raw.decode("utf-8")
        dl_batch_ms = (time.time() - t_dl) * 1000
        print(f"  ⏱ Storage downloads: {dl_batch_ms:.0f}ms ({len(text_files)} file(s))")

        pipeline = CompilerPipeline()
        ranked = []
        all_results = []

        for i, obj in enumerate(text_files):
            filename = obj["name"]
            file_start = time.time()

            resume_text = downloads[filename]

            # Run the full compiler pipeline
            print(
                f"  ▶ Compiling {filename} ({len(resume_text)} chars)...",
                flush=True,
            )
            t0 = time.time()
            result = pipeline.compile(resume_text, job_role)
            compile_ms = (time.time() - t0) * 1000

            score_data = result["score"]
            ranked.append({
                "filename": filename,
                "raw_score": score_data["total_score"],
                "normalized_score": score_data["normalized_score"],
            })

            all_results.append({
                "filename": filename,
                "score": score_data,
                "diagnostics": result["diagnostics"],
                "diagnostics_summary": result["diagnostics_summary"],
                "phases": result["phases"],
                "ir_metadata": result["ir"].get("metadata", {}),
            })

            total_file_ms = (time.time() - file_start) * 1000
            print(
                f"  [{i+1}/{len(text_files)}] {filename}: "
                f"score={score_data['total_score']:.1f}/100 | "
                f"compile={compile_ms:.1f}ms total={total_file_ms:.0f}ms"
            )

        # Sort by normalized score descending
        ranked.sort(key=lambda x: x["normalized_score"], reverse=True)
        all_results.sort(
            key=lambda x: x["score"]["normalized_score"], reverse=True
        )

        # Store in database (with error handling)
        t0 = time.time()
        try:
            clear_resume_table()
            insert_ranked_resumes(ranked, job_role)
            db_ms = (time.time() - t0) * 1000
            print(f"  ⏱ DB save: {db_ms:.0f}ms")
        except Exception as e:
            db_ms = (time.time() - t0) * 1000
            print(f"  ⚠ DB save failed ({db_ms:.0f}ms): {e}")
            # Continue — rankings are still returned in the JSON response

        total_ms = (time.time() - t_start) * 1000
        print(f"✅ Processing complete in {total_ms:.0f}ms")
        print(f"{'='*60}\n")

        return jsonify({
            "status": "success",
            "rankings": ranked,
            "details": all_results,
            "job_role": job_role,
        })
    except Exception as e:
        print(f"ERROR in /process: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/resumes", methods=["GET"])
def list_resumes():
    """
    Lightweight list for the Parsed Results tab (ranked rows from DB).
    """
    try:
        rows = get_ranked_resumes()
        out = []
        for i, r in enumerate(rows):
            fn = r.get("filename") or ""
            out.append(
                {
                    "id": i + 1,
                    "name": fn.rsplit(".", 1)[0] if fn else "Unknown",
                    "email": "",
                    "phone": "",
                    "skills": [],
                    "fileName": fn,
                    "uploadDate": "",
                    "normalized_score": r.get("normalized_score"),
                    "job_role": r.get("job_role"),
                }
            )
        return jsonify(out)
    except Exception as e:
        print(f"ERROR in /resumes: {e}")
        return jsonify([])


@app.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        rankings = get_ranked_resumes()

        if not rankings:
            return jsonify({"status": "error", "message": "No rankings found"}), 404

        return jsonify({"status": "success", "rankings": rankings})
    except Exception as e:
        print(f"ERROR in /rankings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/download-ranked-resumes', methods=['GET'])
def download_ranked_resumes():
    try:
        text_files = supabase.storage.from_("resumes").list("text")
        if not text_files:
            return jsonify({"status": "error", "message": "No processed resumes to download"}), 404

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for obj in text_files:
                name = obj.get("name")
                if not name or not name.endswith(".txt"):
                    continue
                content = supabase.storage.from_("resumes").download(f"text/{name}")
                zf.writestr(name, content)

        buffer.seek(0)
        return app.response_class(
            buffer.getvalue(),
            mimetype="application/zip",
            headers={"Content-Disposition": "attachment; filename=ranked_resumes.zip"},
        )
    except Exception as e:
        print(f"ERROR in /download-ranked-resumes: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8000"))
    app.run(debug=False, port=port)

from databas.resume_store import clear_resume_table, insert_ranked_resumes
from databas.resume_store import get_ranked_resumes
from supabase_utils.supabase_client import supabase

def clear_supabase_folders(bucket_name="resumes"):
    for folder in ["originals", "text"]:
        objects = supabase.storage.from_(bucket_name).list(folder)
        if objects:
            full_paths = [f"{folder}/{obj['name']}" for obj in objects]
            print(f"Deleting from {folder}/:", full_paths)
            supabase.storage.from_(bucket_name).remove(full_paths)
            print(f"✅ Cleared {folder}/ folder in Supabase bucket.")
        else:
            print(f"No files found in {folder}/.")


clear_resume_table()
clear_supabase_folders()
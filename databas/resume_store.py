from databas.db import get_connection
import psycopg2
from psycopg2.extras import execute_values


def get_ranked_resumes():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT filename, job_role, normalized_score
        FROM ranked_resumes
        ORDER BY normalized_score DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    colnames = [desc[0] for desc in cursor.description]
    ranked = [dict(zip(colnames, row)) for row in rows]

    cursor.close()
    return ranked


def clear_resume_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE ranked_resumes")
    conn.commit()
    cur.close()
    print("cleaned the table")


def insert_ranked_resumes(resumes, job_role):
    """
    Batch-insert ranked resumes in a single query.
    resumes: List of dicts with keys 'filename' and 'normalized_score'
    job_role: The job role string used in the ranking
    """
    if not resumes:
        return

    conn = get_connection()
    cur = conn.cursor()

    values = [
        (r['filename'], r['normalized_score'], job_role)
        for r in resumes
    ]

    execute_values(
        cur,
        "INSERT INTO ranked_resumes (filename, normalized_score, job_role) VALUES %s",
        values,
    )

    conn.commit()
    cur.close()
    print(f"✅ Inserted {len(resumes)} ranked resume(s) in one batch.")

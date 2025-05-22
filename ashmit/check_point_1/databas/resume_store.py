from databas.db import get_connection
import psycopg2
from psycopg2.extras import RealDictCursor

def get_ranked_resumes():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT filename, job_role, normalized_score
        FROM resumes
        ORDER BY normalized_score DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    colnames = [desc[0] for desc in cursor.description]
    ranked = [dict(zip(colnames, row)) for row in rows]

    cursor.close()
    conn.close()
    return ranked


def clear_resume_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE resumes")
    print("cleaned the table")
    conn.commit()
    cur.close()
    conn.close()

def insert_ranked_resumes(resumes, job_role):
    """
    resumes: List of dicts with keys 'filename' and 'normalized_score'
    job_role: The job role string used in the ranking
    """
    conn = get_connection()
    cur = conn.cursor()
    
    for resume in resumes:
        cur.execute("""
            INSERT INTO resumes (filename, normalized_score, job_role)
            VALUES (%s, %s, %s)
        """, (resume['filename'], resume['normalized_score'], job_role))
    
    conn.commit()
    cur.close()
    conn.close()

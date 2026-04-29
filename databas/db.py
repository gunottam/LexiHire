import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ── Singleton connection with timeout ─────────────────────────────────────
_conn = None


def get_connection():
    """
    Return a reusable database connection.
    Creates one on first call and reuses it, avoiding repeated DNS lookups.
    Includes a 5-second connect timeout to prevent hanging.
    """
    global _conn
    if _conn is None or _conn.closed:
        db_url = os.environ["SUPABASE_DB_URL"]
        _conn = psycopg2.connect(db_url, connect_timeout=5)
        _conn.autocommit = False
        print("✅ Database connection established.")
    return _conn


def close_connection():
    """Close the singleton connection if open."""
    global _conn
    if _conn and not _conn.closed:
        _conn.close()
        _conn = None

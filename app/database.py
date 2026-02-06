import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "appointments.db"

def init_db():
    print(f"👉 SQLITE DB PATH: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            name TEXT,
            phone TEXT,
            reason TEXT,
            date_text TEXT,
            date_iso TEXT,
            half_day TEXT,
            time_text TEXT,
            time_24h TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

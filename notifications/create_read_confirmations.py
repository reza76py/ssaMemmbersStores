# create_read_confirmations.py

import sqlite3
from data.db import get_connection

def create_read_confirmation_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS read_confirmations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            confirmed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ read_confirmations table ensured.")

if __name__ == "__main__":
    create_read_confirmation_table()

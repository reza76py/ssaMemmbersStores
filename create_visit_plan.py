# create_visit_plan.py

import sqlite3
from data.db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS visit_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    store_name TEXT NOT NULL,
    visit_date TEXT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES people(id)
)
""")

conn.commit()
conn.close()
print("✅ visit_plan table ensured.")

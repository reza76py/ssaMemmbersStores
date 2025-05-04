# alter_people_add_email.py

import sqlite3

conn = sqlite3.connect("ssa_app.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE people ADD COLUMN email TEXT DEFAULT ''")
    conn.commit()
    print("✅ 'email' column successfully added to 'people' table.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Error: {e}")
finally:
    conn.close()

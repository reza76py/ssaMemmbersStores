# inspect_people_table.py

import sqlite3

conn = sqlite3.connect("ssa_app.db")
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='people'")
result = cursor.fetchone()

print("People table schema:\n")
print(result[0] if result else "Table not found.")

conn.close()

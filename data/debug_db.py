import sqlite3

conn = sqlite3.connect("ssa_app.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM people")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()

from data.db import get_connection

conn = get_connection()
rows = conn.execute("SELECT id, name, email FROM people").fetchall()
for row in rows:
    print(row)
conn.close()
# inspect_read_confirmations.py
from data.db import get_connection

conn = get_connection()
cursor = conn.cursor()
rows = cursor.execute("SELECT * FROM read_confirmations").fetchall()

for row in rows:
    print(row)
conn.close()

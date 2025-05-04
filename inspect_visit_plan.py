# inspect_visit_plan.py
from data.db import get_connection

conn = get_connection()
cursor = conn.cursor()
rows = cursor.execute("SELECT * FROM visit_plan").fetchall()

for row in rows:
    print(row)

conn.close()

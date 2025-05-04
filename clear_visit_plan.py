from data.db import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM visit_plan")
conn.commit()
conn.close()
print("✅ Cleared visit_plan table.")
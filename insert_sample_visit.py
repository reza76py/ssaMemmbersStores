# insert_sample_visit.py

from data.db import get_connection

# Change these values as needed
person_name = "Reza"   # This must match an existing name in your people table
store_name = "Bunnings Newstead"
visit_date = "2025-05-06"

conn = get_connection()
cursor = conn.cursor()

# Find the person's ID based on the name
cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
person = cursor.fetchone()

if person:
    person_id = person[0]
    cursor.execute("""
        INSERT INTO visit_plan (person_id, store_name, visit_date)
        VALUES (?, ?, ?)
    """, (person_id, store_name, visit_date))
    conn.commit()
    print("✅ Sample visit assignment added.")
else:
    print("❌ Person not found. Please check the name in your people table.")

conn.close()

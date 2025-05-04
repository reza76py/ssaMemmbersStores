import sqlite3

# Connect to your SSA database
conn = sqlite3.connect("ssa_app.db")
cursor = conn.cursor()

# Query all records from read_confirmations table
cursor.execute("SELECT * FROM read_confirmations")
rows = cursor.fetchall()

# Print results
print("📋 Read Confirmations:")
for row in rows:
    print(row)

conn.close()

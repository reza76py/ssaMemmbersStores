import sqlite3

# Database file name
DB_NAME = "ssa_app.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def initialize_database():
    """Create tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS read_confirmations")

    # Create People table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT CHECK(role IN ('leader', 'member')) NOT NULL,
        email TEXT NOT NULL,
        latitude REAL,
        longitude REAL
    )
    """)

    # Create Stores table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        latitude REAL,
        longitude REAL
    )
    """)

    # Create Deliveries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_id INTEGER,
        goods_value REAL,
        date TEXT,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)

    # Create Availability table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER,
        available INTEGER,
        date TEXT,
        FOREIGN KEY(person_id) REFERENCES people(id)
    )
    """)

    # Create Visit Log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        store_id INTEGER,
        leader_id INTEGER,
        members TEXT, -- CSV format (e.g., "M1,M2")
        FOREIGN KEY(store_id) REFERENCES stores(id),
        FOREIGN KEY(leader_id) REFERENCES people(id)
    )
    """)

    # Create Read Confirmations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS read_confirmations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER,
        store_name TEXT,
        visit_date TEXT,
        FOREIGN KEY(person_id) REFERENCES people(id)
    )
    """)


    conn.commit()
    conn.close()

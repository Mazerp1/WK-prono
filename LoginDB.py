import sqlite3

conn = sqlite3.connect("login.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS registrants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sport TEXT NOT NULL
)
""")

conn.commit()
conn.close()
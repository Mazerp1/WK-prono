import sqlite3

conn = sqlite3.connect("wk_prono.db")
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE users
    ADD COLUMN league_id INTEGER
""")

conn.commit()
conn.close()

print("Added league_id")
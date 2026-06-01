import sqlite3

conn = sqlite3.connect("wk_prono.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# PICKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    country TEXT NOT NULL,
    factor INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE(user_id, country)
)
""")

# MATCHES
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_id INTEGER UNIQUE,
    league_id INTEGER,
    home_team TEXT,
    away_team TEXT,
    home_goals INTEGER,
    away_goals INTEGER,
    status TEXT,
    matchday INTEGER,
    is_finished INTEGER DEFAULT 0,
    kickoff TEXT
)
""")

# LEAGUES
cursor.execute("""
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    type TEXT,
    logo TEXT,
    season INTEGER
)
""")

conn.commit()
conn.close()
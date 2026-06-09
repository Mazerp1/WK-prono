import sqlite3

conn = sqlite3.connect("wk_prono.db")
cursor = conn.cursor()

cursor.executescript("""
-- USERS
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    league_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COUNTRIES (teams in your case)
CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    dutch_name TEXT,
    score INTEGER DEFAULT 0
);

-- PICKS (user predictions)
CREATE TABLE IF NOT EXISTS picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    country_id INTEGER NOT NULL,
    factor INTEGER NOT NULL,

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(country_id) REFERENCES countries(id),

    UNIQUE(user_id, country_id)
);

-- MATCHES (API data storage)
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_match_id INTEGER UNIQUE,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_goals INTEGER,
    away_goals INTEGER,
    status TEXT,
    match_date TEXT,
    is_finished INTEGER DEFAULT 0
);

-- PROCESSED MATCHES (prevents double scoring)
CREATE TABLE IF NOT EXISTS processed_matches (
    api_match_id INTEGER PRIMARY KEY
);

-- league
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    join_code TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()

print("Database created successfully")
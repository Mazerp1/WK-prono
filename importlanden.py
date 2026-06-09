import sqlite3
import requests

API_URL = "https://api.football-data.org/v4/competitions/2000/matches"

HEADERS = {
    "x-apisports-key": "5f7025a48bab43e89584361fb4f253e7"
}

response = requests.get(API_URL, headers=HEADERS)
data = response.json()

conn = sqlite3.connect("wk_prono.db")
cursor = conn.cursor()

for item in data["response"]:
    team = item["team"]

    api_id = team["id"]
    name = team["name"]

    cursor.execute("""
        INSERT OR IGNORE INTO countries (id, name, score)
        VALUES (?, ?, 0)
    """, (api_id, name))

conn.commit()
conn.close()

print("API landen succesvol geïmporteerd")
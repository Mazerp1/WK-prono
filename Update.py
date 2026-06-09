import requests
import sqlite3

headers = {
    "X-Auth-Token": "5f7025a48bab43e89584361fb4f253e7"
}

resp = requests.get("https://api.football-data.org/v4/competitions/2000/matches", headers=headers)
data = resp.json()

conn = sqlite3.connect("wk_prono.db")
cursor = conn.cursor()

for m in data["matches"]:

    match_id = m["id"]
    status = m["status"]

    home_id = m["homeTeam"]["id"] if m["homeTeam"] else None
    away_id = m["awayTeam"]["id"] if m["awayTeam"] else None

    score = m.get("score", {}).get("fullTime", {})
    home_goals = score.get("home")
    away_goals = score.get("away")

    # insert/update match (NO duplicates)
    cursor.execute("""
        INSERT OR IGNORE INTO matches (api_match_id)
        VALUES (?)
    """, (match_id,))

    cursor.execute("""
        UPDATE matches
        SET home_team_id=?, away_team_id=?, home_goals=?, away_goals=?, status=?, match_date=?
        WHERE api_match_id=?
    """, (home_id, away_id, home_goals, away_goals, status, m["utcDate"], match_id))

    # process only finished matches once
    cursor.execute("""
        SELECT api_match_id FROM processed_matches WHERE api_match_id=?
    """, (match_id,))

    if status == "FINISHED" and not cursor.fetchone():

        if home_goals > away_goals:
            cursor.execute("UPDATE countries SET score = score + 3 WHERE id=?", (home_id,))
        elif away_goals > home_goals:
            cursor.execute("UPDATE countries SET score = score + 3 WHERE id=?", (away_id,))
        else:
            cursor.execute("UPDATE countries SET score = score + 1 WHERE id IN (?,?)", (home_id, away_id))

        cursor.execute("""
            INSERT INTO processed_matches (api_match_id)
            VALUES (?)
        """, (match_id,))

conn.commit()
conn.close()

print("Sync done")
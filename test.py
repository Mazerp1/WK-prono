import requests

API_KEY = "5f7025a48bab43e89584361fb4f253e7"
url = "https://api.football-data.org/v4/competitions/2021/matches"

headers = {
    "X-Auth-Token": API_KEY
}

response = requests.get(url, headers=headers)

data = response.json()

matches = data.get("matches", [])

print("World Cup matches found:", len(matches))

for m in matches:
    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]
    status = m["status"]
    score = m["score"]["fullTime"]
    winner = m["score"]["winner"]
    home_goals = score["home"]
    away_goals = score["away"]
    date = m["utcDate"]
    if winner == "HOME_TEAM":
        name+= 3
    print(f"{home} vs {away} | {home_goals}-{away_goals} | {status} | {date} | Winner: {winner}")
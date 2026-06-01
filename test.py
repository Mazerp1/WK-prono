import requests
import json

uri = 'https://api.football-data.org/v4/matches'
headers = { 'X-Auth-Token': '5f7025a48bab43e89584361fb4f253e7' }

response = requests.get(uri, headers=headers)
for match in response.json()['matches']:
  print(match)
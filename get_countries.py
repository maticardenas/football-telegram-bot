import json

import requests

url = "https://api-football-v1.p.rapidapi.com/v3/teams/countries"

headers = {
    "X-RapidAPI-Key": "5ba265a165msh53a2d69e9a39774p1216ccjsn55c3104b0b9f",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
}

response = requests.request("GET", url, headers=headers)


data = response.json()

with open("countries.json", "w") as file:
    json.dump(data, file)

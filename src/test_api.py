from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("API_FOOTBALL_KEY")

url = "https://v3.football.api-sports.io/status"

headers = {
    "x-apisports-key": api_key
}

response = requests.get(url, headers=headers)

print(response.status_code)
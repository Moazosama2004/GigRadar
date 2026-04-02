# save as inspect_mostaql.py in your GigRadar/ folder
import requests
from fake_useragent import UserAgent

ua = UserAgent()
headers = {
    "User-Agent": ua.random,
    "Accept-Language": "ar,en;q=0.9",
}

url = "https://mostaql.com/projects?q=python"
response = requests.get(url, headers=headers, timeout=15)
response.encoding = "utf-8"

with open("mostaql_dump.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Status: {response.status_code}")
print(f"Saved {len(response.text)} characters to mostaql_dump.html")

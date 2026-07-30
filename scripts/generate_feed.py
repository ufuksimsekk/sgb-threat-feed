import requests

API_URL = "https://siberguvenlik.gov.tr/api"

params = {
    "type": "ip",
    "per-page": 9999,
    "criticality_level": 4
}

response = requests.get(API_URL, params=params, timeout=60)
response.raise_for_status()

data = response.json()

with open("feeds/ip.txt", "w", encoding="utf-8") as f:
    for item in data["models"]:
        f.write(item["url"] + "\n")

print(f"{len(data['models'])} IP adresi oluşturuldu.")

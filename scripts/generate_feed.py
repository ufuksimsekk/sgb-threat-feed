import requests

BASE_URL = "https://siberguvenlik.gov.tr/api"

params = {
    "type": "ip",
    "page": 0,
    "per-page": 3
}

r = requests.get(BASE_URL, params=params, timeout=60)

print("Status:", r.status_code)
print("Content-Type:", r.headers.get("Content-Type"))
print("Response:")
print(r.text)

r.raise_for_status()

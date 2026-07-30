import requests

BASE_URL = "https://siberguvenlik.gov.tr/api"

all_ips = []

page = 0

while True:

    params = {
        "type": "ip",
        "page": page,
        "per-page": 9999
    }

    r = requests.get(BASE_URL, params=params, timeout=60)
    r.raise_for_status()

    data = r.json()

    models = data.get("models", [])

    if len(models) == 0:
        break

    for item in models:

        ip = item.get("url")

        if ip:
            all_ips.append(ip)

    print(f"Page {page} : {len(models)} kayıt")

    page += 1

with open("feeds/ip.txt","w") as f:

    for ip in sorted(set(all_ips)):

        f.write(ip + "\n")

print(f"Toplam {len(all_ips)} IP")

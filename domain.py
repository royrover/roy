import requests
import json
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/80.0.3987.149 Safari/537.36",
    "Referer": "https://embed-x.eatmorebanana.org/",
    "Origin": "https://embed.bananacake.org",
}

url = (
    "https://embed.bananacake.org/"
    "dooball66v2/ajax_channels.php"
    "?api_key=hmcb4rf66f&sportsonly=1"
)

r = requests.get(url, headers=headers)

soup = BeautifulSoup(r.content, "html.parser")

main = soup.find_all("div", {"class": "col-4 col-md-2 px-1"})

data = []

domains = set()

token = "MTc3OTcyMzk1NHxkYTA0YjQ3OGIxMDc3ZTM1YjZkZWEzOWI5NzA5NzIxMQ"

for channel in main:

    image = channel.find("img").get("src")

    match_id = re.search(r"png\/(.*?)\.png", image)

    if not match_id:
        continue

    channel_id = match_id.group(1)

    player_url = (
        "https://embed-x.eatmorebanana.org/"
        "player_basic.php"
        f"?chat_group="
        f"&api_key=hmcb4rf66f"
        f"&token={token}"
        f"&nopreroll=1"
        f"&muted=1"
        f"&channel={channel_id}"
    )

    try:

        html = requests.get(player_url, headers=headers, timeout=10).text

        match = re.search(r'source\s*:\s*"([^"]+\.m3u8[^"]*)"', html)

        if not match:
            continue

        source_url = match.group(1)

        domain = urlparse(source_url).netloc.split(":")[0]

        print(domain)

        domains.add(domain)

        data.append({"channel_id": channel_id, "domain": domain})

    except Exception as e:
        print(e)

# =========================
# แยกประเภท domain
# =========================

workers_domains = sorted(set(d for d in domains if d.endswith(".workers.dev")))

cdn_domains = sorted(set(d for d in domains if not d.endswith(".workers.dev")))

# =========================
# จำกัดแค่ 4 host
# =========================

workers_domains = workers_domains[:5]
cdn_domains = cdn_domains[:5]

# =========================
# สร้าง JSON
# =========================

result = {
    "workers": {f"host{i+1}": domain for i, domain in enumerate(workers_domains)},
    "cdn": {f"host{i+1}": domain for i, domain in enumerate(cdn_domains)},
}

# =========================
# SAVE
# =========================

with open("hosts.json", "w", encoding="utf-8") as f:

    json.dump(result, f, indent=2, ensure_ascii=False)

print("\nDONE")
print(json.dumps(result, indent=2, ensure_ascii=False))

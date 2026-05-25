import requests
import json
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

HEADERS1 = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",

    "Referer":
        "https://embed.bananacake.org/",
}

HEADERS2 = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",

    "Referer":
        "https://embed-xs.eatmorebanana.org/",
}

API_KEY = "hmcb4rf66f"

CHANNEL_URL = (
    "https://embed.bananacake.org/"
    "dooball66v2/ajax_channels.php"
    f"?api_key={API_KEY}&sportsonly=1"
)

TOKEN_URL = (
    "https://embed.bananacake.org/"
    "dooball66v2/ajax_player.php"
)

PLAYER_URL = (
    "https://embed-xs.eatmorebanana.org/"
    "player_basic.php"
)

print("FETCH CHANNELS...")

r = requests.get(
    CHANNEL_URL,
    headers=HEADERS1,
    timeout=15
)

print("STATUS:", r.status_code)

soup = BeautifulSoup(r.content, "html.parser")

main = soup.find_all(
    "div",
    {"class": "col-4 col-md-2 px-1"}
)

print("TOTAL:", len(main))

domains = set()

for channel in main:

    try:

        img = channel.find("img")

        if not img:
            continue

        image = img.get("src", "")

        match_id = re.search(
            r"png\/(.*?)\.png",
            image
        )

        if not match_id:
            continue

        channel_id = match_id.group(1)

        print("\n===================")
        print("CHANNEL:", channel_id)

        # =========================
        # GET TOKEN
        # =========================

        token_api = (
            f"{TOKEN_URL}"
            f"?channel={channel_id}"
            f"&api_key={API_KEY}"
        )

        token_res = requests.get(
            token_api,
            headers=HEADERS1,
            timeout=15
        )

        token_html = token_res.text

        token_match = re.search(
            r'token[=:]([a-zA-Z0-9_\-\.]+)',
            token_html
        )

        token = (
            token_match.group(1)
            if token_match
            else None
        )

        print("TOKEN:", token)

        if not token:
            print("NO TOKEN")
            continue

        # =========================
        # PLAYER
        # =========================

        player_url = (
            f"{PLAYER_URL}"
            f"?chat_group="
            f"&api_key={API_KEY}"
            f"&token={token}"
            f"&nopreroll=1"
            f"&muted=1"
            f"&channel={channel_id}"
        )

        player_res = requests.get(
            player_url,
            headers=HEADERS2,
            timeout=15
        )

        html = player_res.text

        matches = re.findall(
            r'https?:\/\/[^"\']+\.m3u8[^"\']*',
            html,
            re.I
        )

        if not matches:
            print("NO M3U8")
            continue

        source_url = matches[0]

        print("SOURCE:", source_url)

        domain = (
            urlparse(source_url)
            .netloc
            .split(":")[0]
        )

        print("DOMAIN:", domain)

        domains.add(domain)

    except Exception as e:

        print("ERROR:", e)

# =========================
# SPLIT DOMAIN
# =========================

workers_domains = sorted(set(
    d for d in domains
    if d.endswith(".workers.dev")
))

cdn_domains = sorted(set(
    d for d in domains
    if not d.endswith(".workers.dev")
))

workers_domains = workers_domains[:5]
cdn_domains = cdn_domains[:5]

# =========================
# JSON
# =========================

result = {

    "workers": {
        f"host{i+1}": domain
        for i, domain in enumerate(workers_domains)
    },

    "cdn": {
        f"host{i+1}": domain
        for i, domain in enumerate(cdn_domains)
    }
}

# =========================
# SAVE
# =========================

with open(
    "hosts.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\n===================")
print("FINAL RESULT")
print("===================")

print(json.dumps(
    result,
    indent=2,
    ensure_ascii=False
))


import os
import re
import json
import time
import requests

from urllib.parse import urlparse, parse_qs

# ==========================================
# CONFIG
# ==========================================

WORKER_URL = (
    "https://livescorethai9.m3-navthai.workers.dev/"
)

API_URL = (
    "https://embed-xlb.cremedebanana.org/api/v1/playback/start"
)

API_KEY = os.environ.get("API_KEY", "")

VIEWER_ID = "7082c578da034ad78c6574168f9c5493"

TARGET_CHANNEL = "bein-sport-3-au"

# ==========================================
# REQUEST ID
# ==========================================

def base36(number):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""

    while number:
        number, remainder = divmod(number, 36)
        result = chars[remainder] + result

    return result or "0"


request_id = (
    VIEWER_ID
    + base36(int(time.time() * 1000))
)

# ==========================================
# GET M3U FROM WORKER
# ==========================================

print("1. Fetching Worker M3U...")

try:
    response = requests.get(
        WORKER_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/157.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "th,en;q=0.9"
        },
        timeout=30
    )

    print("Worker HTTP:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Response size:", len(response.content))

    if response.status_code != 200:
        print("\nWORKER RESPONSE BODY:")
        print(response.text[:5000])
        raise SystemExit(1)

    playlist = response.text

    if "#EXTM3U" not in playlist:
        print("ERROR: Invalid M3U response")
        print(playlist[:3000])
        raise SystemExit(1)

    print("Worker M3U: OK")

except requests.RequestException as e:
    print("WORKER ERROR:", str(e))
    raise SystemExit(1)


# ==========================================
# PARSE CHANNELS
# ==========================================

print("\n2. Parsing playlist...")

entries = []
current_info = None

for line in playlist.splitlines():

    line = line.strip()

    if line.startswith("#EXTINF:"):
        current_info = line

    elif line.startswith("#EXTVLCOPT:"):
        continue

    elif line and not line.startswith("#") and current_info:

        parsed = urlparse(line)
        params = parse_qs(parsed.query)

        match_id = params.get("match_id", [""])[0]
        channel = params.get("channel", [""])[0]

        if match_id and channel:
            entries.append({
                "info": current_info,
                "url": line,
                "match_id": match_id,
                "channel": channel
            })

        current_info = None

print("Channels found:", len(entries))

if not entries:
    print("ERROR: No valid channels found")
    raise SystemExit(1)

# ==========================================
# SELECT CHANNEL
# ==========================================

selected = next(
    (
        item for item in entries
        if item["channel"] == TARGET_CHANNEL
    ),
    entries[0]
)

channel = selected["channel"]
match_id = selected["match_id"]

print("\n3. Selected channel")
print("Channel:", channel)
print("Match ID:", match_id)

# ==========================================
# CHECK API KEY
# ==========================================

if not API_KEY:
    print("ERROR: API_KEY secret is missing")
    raise SystemExit(1)

# ==========================================
# PAYLOAD
# ==========================================

payload = {
    "api_key": API_KEY,
    "match_id": match_id,
    "channel": channel,
    "viewer_id": VIEWER_ID,
    "request_id": request_id
}

# ==========================================
# HEADERS
# ==========================================

headers = {
    "Accept": "*/*",
    "Accept-Language": "th,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://livescorethai.football",
    "Priority": "u=1, i",
    "Referer": "https://livescorethai.football/",
    "Sec-CH-UA": '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/157.0.0.0 Safari/537.36"
    )
}

# ==========================================
# PLAYBACK API
# ==========================================

print("\n4. Calling Playback API...")

try:

    api_response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=30
    )

    print("API HTTP:", api_response.status_code)

    try:
        data = api_response.json()
    except ValueError:
        data = None

    if api_response.status_code != 200:

        print("API ERROR")
        print("Response:", json.dumps(
            data if data is not None else api_response.text[:2000],
            ensure_ascii=False,
            indent=2
        ))

        raise SystemExit(1)

    if not isinstance(data, dict):

        print("ERROR: Invalid JSON response")
        raise SystemExit(1)

    master_url = (
        data.get("session", {})
        .get("urls", {})
        .get("master", "")
    )

    if not master_url:

        print("ERROR: Master URL not found")
        print(json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )[:4000])

        raise SystemExit(1)

    print("\n================================")
    print("PLAYBACK SUCCESS")
    print("================================")
    print("Channel:", channel)
    print("Match ID:", match_id)
    print("Master URL received: YES")
    print("Master host:", urlparse(master_url).netloc)
    print("================================")

except requests.RequestException as e:

    print("REQUEST ERROR:", str(e))
    raise SystemExit(1)

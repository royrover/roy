
import os
import time
import requests

API_URL = "https://embed-xlb.cremedebanana.org/api/v1/playback/start"

API_KEY = os.environ["API_KEY"]

viewer_id = "7082c578da034ad78c6574168f9c5493"

request_id = viewer_id + base36(
    int(time.time() * 1000)
)

def base36(number):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""

    while number:
        number, remainder = divmod(number, 36)
        result = chars[remainder] + result

    return result or "0"

payload = {
    "api_key": API_KEY,
    "match_id": "6af897877d8cfc8942016332",
    "channel": "bein-sport-3-au",
    "viewer_id": viewer_id,
    "request_id": request_id
}

headers = {
    "Accept": "*/*",
    "Accept-Language": "th,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://livescorethai.football",
    "Referer": "https://livescorethai.football/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
}

print("Testing Playback API...")

try:
    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=30
    )

    print("HTTP:", response.status_code)

    data = response.json()

    master = data.get("session", {}).get("urls", {}).get("master", "")

    if response.status_code == 200 and master:
        print("SUCCESS: MASTER RECEIVED")
        print("Master host:", requests.utils.urlparse(master).netloc)
    else:
        print("FAILED")
        print("Response:", response.text[:3000])

except Exception as e:
    print("ERROR:", str(e))
    raise SystemExit(1)

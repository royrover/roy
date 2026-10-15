import json
import re
import requests

ACCOUNT_ID = "6415628290001"
VIDEO_ID = "6392745120112"
PLAYER_EMBED_ID = "7eqSlPOCLA_default"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.oned.net/",
    "Origin": "https://www.oned.net",
}

def run():
    print("1. Fetching player JS to get Policy Key...")
    js_url = f"https://players.brightcove.net/{ACCOUNT_ID}/{PLAYER_EMBED_ID}/index.min.js"
    res = requests.get(js_url, headers=headers)
    
    if res.status_code != 200:
        raise Exception(f"Failed to fetch player JS: {res.status_code}")

    match = re.search(r'(BCpk[a-zA-Z0-9_\-\.]+)', res.text)
    if not match:
        raise Exception("Policy Key not found in JS.")
    
    policy_key = match.group(1)
    print(f"Policy Key found: {policy_key[:15]}...")

    print("2. Requesting stream URL from Brightcove API...")
    api_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/{VIDEO_ID}"
    api_headers = {
        "Accept": f"application/json;pk={policy_key}",
        "Origin": "https://www.oned.net",
        "Referer": "https://www.oned.net/",
    }

    api_res = requests.get(api_url, headers=api_headers)
    if api_res.status_code != 200:
        raise Exception(f"API request failed: {api_res.status_code} - {api_res.text}")

    data = api_res.json()
    sources = data.get("sources", [])
    
    stream_url = None
    for src in sources:
        # หาลิงก์ที่เป็น HLS (.m3u8)
        if src.get("type") == "application/x-mpegURL" or ".m3u8" in src.get("src", ""):
            stream_url = src.get("src")
            break

    if not stream_url:
        raise Exception("HLS Stream URL not found in API response.")

    print(f"Captured Stream URL: {stream_url}")

    # 3. บันทึกลง gmm25.json
    output_data = {"stream_url": stream_url}
    with open("gmm25.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("Successfully updated gmm25.json!")

if __name__ == "__main__":
    run()

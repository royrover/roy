import base64
from datetime import datetime
import json
import re
import cloudscraper


def get_rumble_hls():
  scraper = cloudscraper.create_scraper(
      browser={"browser": "chrome", "platform": "windows", "desktop": True}
  )
  url = "https://rumble.com/embed/v7ew6ko"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Referer": "https://rumble.com",
  }

  try:
    response = scraper.get(url, headers=headers, timeout=15)
    html = response.text

    match = re.search(r'"hls"\s*:\s*\{\s*"url"\s*:\s*"([^"]+)"', html)
    if match:
      hls_url = match.group(1).replace(r"\/", "/")
      b64_encoded = base64.b64encode(hls_url.encode("utf-8")).decode("utf-8")
      return b64_encoded
  except Exception as e:
    print(f"Error: {e}")

  return None


if __name__ == "__main__":
  b64_result = get_rumble_hls()

  # สร้างโครงสร้างข้อมูล JSON
  data = {
      "status": "success" if b64_result else "error",
      "base64": b64_result,
      "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }

  # บันทึกลงไฟล์ wp64.json
  with open("wp64.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

  print("✅ Saved to wp64.json successfully!")

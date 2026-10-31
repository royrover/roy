import base64
import re
import cloudscraper


def get_rumble_hls():
  # สร้าง scraper instance ที่จำลองบราวเซอร์ Chrome บน Windows
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

    # ค้นหา HLS URL ด้วย Regex
    match = re.search(r'"hls"\s*:\s*\{\s*"url"\s*:\s*"([^"]+)"', html)
    if match:
      hls_url = match.group(1).replace(r"\/", "/")
      # แปลงเป็น Base64
      b64_encoded = base64.b64encode(hls_url.encode("utf-8")).decode("utf-8")
      return b64_encoded

  except Exception as e:
    print(f"Error: {e}")

  return None


if __name__ == "__main__":
  result = get_rumble_hls()
  if result:
    print(result)
  else:
    print("ERROR_NOT_FOUND")

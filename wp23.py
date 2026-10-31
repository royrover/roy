import base64
from datetime import datetime
import json
import re
from playwright.sync_api import sync_playwright


def get_rumble_hls():
  with sync_playwright() as p:
    # เปิดใช้งาน Browser แบบ Headless
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    )
    page = context.new_page()

    try:
      # เข้าหน้า Embed ของ Rumble
      page.goto(
          "https://rumble.com/embed/v7ew6ko",
          wait_until="networkidle",
          timeout=30000,
      )

      # รอให้ Cloudflare challenge ผ่านและหน้าเว็บโหลดเสร็จ
      page.wait_for_timeout(4000)

      html = page.content()
      browser.close()

      # ค้นหา HLS URL ด้วย Regex
      match = re.search(r'"hls"\s*:\s*\{\s*"url"\s*:\s*"([^"]+)"', html)
      if match:
        hls_url = match.group(1).replace(r"\/", "/")
        b64_encoded = base64.b64encode(hls_url.encode("utf-8")).decode("utf-8")
        return b64_encoded

    except Exception as e:
      print(f"Playwright Error: {e}")
      browser.close()

  return None


if __name__ == "__main__":
  b64_result = get_rumble_hls()

  data = {
      "status": "success" if b64_result else "error",
      "base64": b64_result,
      "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }

  with open("wp64.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

  print("✅ Updated wp64.json via Playwright!")

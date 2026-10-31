import base64
from datetime import datetime
import json
import re
from playwright.sync_api import sync_playwright


def get_rumble_hls():
  with sync_playwright() as p:
    # 📌 เพิ่ม Arguments สำหรับ Linux Runner บน GitHub Actions โดยเฉพาะ
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--headless=new",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
        ],
    )

    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
    )

    # ซ่อนความเป็นบอท
    context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    page = context.new_page()

    try:
      print("🌐 กำลังเปิดหน้าเว็บผ่าน Playwright...")
      page.goto(
          "https://rumble.com/embed/v7ew6ko",
          wait_until="domcontentloaded",
          timeout=40000,
      )

      # 📌 รอเผื่อ Cloudflare เปลี่ยนหน้าหรือโหลดสคริปต์ (เพิ่มเวลาเป็น 8 วินาที)
      page.wait_for_timeout(8000)

      html = page.content()

      # (ทางเลือก) พรินต์ความยาว HTML ออกมาดูใน Log ของ GitHub ว่าดึงมาได้จริงไหม
      print(f"📄 ความยาว HTML ที่ดึงมาได้: {len(html)} ตัวอักษร")

      browser.close()

      # ค้นหา HLS URL ด้วย Regex
      match = re.search(r'"hls"\s*:\s*\{\s*"url"\s*:\s*"([^"]+)"', html)
      if match:
        hls_url = match.group(1).replace(r"\/", "/")
        b64_encoded = base64.b64encode(hls_url.encode("utf-8")).decode("utf-8")
        return b64_encoded

    except Exception as e:
      print(f"❌ Playwright Error: {e}")
      try:
        browser.close()
      except:
        pass

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

  if b64_result:
    print("✅ Success: บันทึกลง wp64.json เรียบร้อย")
  else:
    print(
        "❌ Error: ไม่สามารถดึงลิงก์ได้ (อาจยังติด Cloudflare บน GitHub Actions)"
    )

import json
import os
from playwright.sync_api import sync_playwright

def run():
    captured_url = None
    
    with sync_playwright() as p:
        # รันแบบเปิดหัวข้อจำลอง (หรือปิด headless ถ้าอยากลองรันดูในเครื่องตัวเอง)
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        # สร้าง Context พร้อมกำหนด User-Agent ที่เป็นเบราว์เซอร์จริง และขนาดจอ
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True
        )
        
        page = context.new_page()

        def handle_request(route, request):
            nonlocal captured_url
            if "fastly.live.brightcove.com" in request.url and ".m3u8" in request.url:
                if not captured_url:
                    captured_url = request.url
                    print(f"Captured Stream URL: {captured_url}")
            route.continue_()

        page.route("**/*", handle_request)

        print("Navigating to oned.net...")
        try:
            # ใช้ domcontentloaded หรือ networkidle เพื่อรอให้หน้าเว็บโหลดสมบูรณ์
            page.goto("https://www.oned.net/live-tv/gmm25", timeout=60000, wait_until="networkidle")
            
            # เลื่อนหน้าจอลงเล็กน้อยเพื่อให้เกิด Event กระตุ้นการเล่นวิดีโอ (ถ้ามี)
            page.mouse.wheel(0, 300)
            
            # เพิ่มเวลารอให้แน่ใจว่าเครื่องเล่น (Player) ถูกกระตุ้นและยิงสตรีมออกมา
            page.wait_for_timeout(20000)
            
        except Exception as e:
            print(f"Error loading page: {e}")
        
        browser.close()

    if captured_url:
        data = {"stream_url": captured_url}
        with open("gmm25.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Updated gmm25.json successfully!")
    else:
        raise Exception("Could not capture the stream URL!")

if __name__ == "__main__":
    run()

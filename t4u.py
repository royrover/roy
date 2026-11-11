import re
from playwright.sync_api import sync_playwright

def get_data():
    with sync_playwright() as p:
        # เปิดเบราว์เซอร์แบบ headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print("กำลังเปิดเว็บไซต์ True4u ผ่าน Playwright เพื่อผ่านระบบป้องกัน...")
            # เข้าหน้าแรกก่อนเพื่อให้ Cloudflare ผ่านการตรวจสอบ (Challenge)
            page.goto("https://true4u.com/", wait_until="domcontentloaded", timeout=60000)
            
            # รอหรือเข้าไปที่ API endpoint โดยตรงผ่านหน้าเว็บที่เปิดอยู่
            print("กำลังดึง API signer-url...")
            response = page.goto("https://true4u.com/live-api/signer-url?prefix=/live/", wait_until="domcontentloaded", timeout=30000)
            
            if response and response.status == 200:
                raw_url = page.inner_text("body") # ดึงข้อความ URL จากหน้าเว็บ
                
                # ทำความสะอาดข้อความ เผื่อติด HTML tags
                raw_url = raw_url.strip()
                
                # แปลงจาก Master Playlist เป็น 720p
                final_url = re.sub(r"playlist\.m3u8", "pl_720p/index.m3u8", raw_url)
                
                # เซฟลงไฟล์ data.json
                with open("data.json", "w", encoding="utf-8") as f:
                    f.write(final_url)
                    
                print(f"Success! URL saved to data.json")
                print(f"URL: {final_url}")
            else:
                status = response.status if response else "Unknown"
                print(f"Failed with status code: {status}")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_data()

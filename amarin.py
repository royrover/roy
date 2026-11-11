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
            print("กำลังเปิดเว็บไซต์ Amarin TV ผ่าน Playwright...")
            page.goto("https://www.amarintv.com/live", wait_until="domcontentloaded", timeout=60000)
            
            # ดึง Source Code ทั้งหน้าเว็บมาวิเคราะห์
            html_content = page.content()
            
            # ค้นหาลิงก์ m3u8 ที่อยู่ในฟิลด์ source ของ live
            match = re.search(r'"source"\s*:\s*"(https:[^"]+\.m3u8[^"]*)"', html_content)
            
            if match:
                raw_url = match.group(1)
                
                # แปลงรหัส Unicode escape เช่น \u0026 ให้เป็น & ปกติ
                final_url = raw_url.encode().decode('unicode_escape')
                final_url = final_url.replace('\\', '').strip()
                
                # เขียนลงไฟล์ amarin.json
                with open("amarin.json", "w", encoding="utf-8") as f:
                    f.write(final_url)
                    
                print(f"✅ Success! URL saved: {final_url}")
            else:
                print("❌ No M3U8 found in page source.")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_data()

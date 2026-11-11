import re
from playwright.sync_api import sync_playwright

def get_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print("กำลังเปิดเว็บไซต์ Amarin TV ผ่าน Playwright...")
            page.goto("https://www.amarintv.com/live", wait_until="networkidle", timeout=60000)
            
            # 🛑 เพิ่มการสั่งรอให้ข้อความหรือโครงสร้างที่เกี่ยวกับ m3u8 ปรากฏบนหน้าเว็บก่อน
            print("กำลังรอให้หน้าเว็บโหลดข้อมูลสตรีม...")
            try:
                page.wait_for_selector("script", timeout=10000)
            except:
                pass
            
            # ดึง Source Code ทั้งหน้าเว็บหลังจากโหลดเสร็จสมบูรณ์
            html_content = page.content()
            
            # ค้นหาลิงก์ m3u8 จากฟิลด์ source ใน JSON ของหน้าเว็บ
            match = re.search(r'"source"\s*:\s*"(https:[^"]+\.m3u8[^"]*)"', html_content)
            
            if match:
                raw_url = match.group(1)
                
                # แปลงรหัส \u0026 ให้กลับเป็น & ปกติ และล้างเครื่องหมาย \ ส่วนเกินออก
                final_url = raw_url.encode().decode('unicode_escape').replace('\\', '').strip()
                
                # เขียนลงไฟล์ amarin.json
                with open("amarin.json", "w", encoding="utf-8") as f:
                    f.write(final_url)
                    
                print(f"✅ Success! URL saved: {final_url}")
            else:
                print("❌ No M3U8 found in page source after waiting.")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_data()

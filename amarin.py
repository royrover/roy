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
            print("🔍 [DEBUG] กำลังเปิดเว็บไซต์ Amarin TV ผ่าน Playwright...")
            page.goto("https://www.amarintv.com/live", wait_until="domcontentloaded", timeout=60000)
            
            # รอให้ JavaScript โหลดข้อมูลสักครู่
            print("⏳ [DEBUG] รอหน้าเว็บเรนเดอร์ข้อมูล (5 วินาที)...")
            page.wait_for_timeout(5000)
            
            # ดึง HTML ทั้งหมดออกมา
            html_content = page.content()
            
            # 📝 บันทึก HTML ลงไฟล์ เพื่อให้เราเปิดดูใน GitHub Artifacts หรือเช็คย้อนหลังได้
            with open("debug_amarin.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("💾 [DEBUG] บันทึกหน้าเว็บลงไฟล์ debug_amarin.html เรียบร้อยแล้ว")
            
            # ลองค้นหาคำว่า m3u8 หรือ source ใน HTML แบบไม่สนใจตัวพิมพ์เล็กใหญ่
            if "m3u8" in html_content:
                print("🎯 [DEBUG] พบคำว่า 'm3u8' ในหน้าเว็บแล้ว กำลังแกะลิงก์...")
            else:
                print("⚠️ [DEBUG] ไม่พบคำว่า 'm3u8' ใน HTML หน้าเว็บเลย อาจจะถูกโหลดแบบ Dynamic หรือเปลี่ยนโครงสร้าง")

            # ค้นหาด้วย Regex
            match = re.search(r'"source"\s*:\s*"(https:[^"]+\.m3u8[^"]*)"', html_content)
            
            if match:
                raw_url = match.group(1)
                final_url = raw_url.encode().decode('unicode_escape').replace('\\', '').strip()
                
                with open("amarin.json", "w", encoding="utf-8") as f:
                    f.write(final_url)
                    
                print(f"✅ Success! URL saved: {final_url}")
            else:
                print("❌ No M3U8 found via regex. (ลองเช็คไฟล์ debug_amarin.html ดูโครงสร้างจริงกัน)")
                # พิมพ์ตัวอย่างข้อความสั้นๆ ใน HTML ออกมาดูคร่าวๆ ใน Log
                print(f"📄 ตัวอย่าง HTML บางส่วน (ความยาวรวม {len(html_content)} ตัวอักษร):")
                print(html_content[:500])
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_data()

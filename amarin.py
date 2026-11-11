from playwright.sync_api import sync_playwright

def get_data():
    stream_url = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 🎯 ฟังก์ชันดักจับ Request ทั้งหมด ถ้าอันไหนมี .m3u8 ให้เก็บไว้ทันที
        def handle_request(request):
            nonlocal stream_url
            if ".m3u8" in request.url:
                stream_url = request.url

        page.on("request", handle_request)
        
        try:
            print("🔍 กำลังเปิดเว็บไซต์ Amarin TV และดักจับลิงก์สตรีม...")
            page.goto("https://www.amarintv.com/live", wait_until="domcontentloaded", timeout=60000)
            
            # รอเวลาให้หน้าเว็บรัน Player และยิง Request ออกมา (ประมาณ 6 วินาที)
            page.wait_for_timeout(6000)
            
            if stream_url:
                # ทำความสะอาดลิงก์ถ้ามีเครื่องหมาย \ ปะปน
                final_url = stream_url.replace('\\', '').strip()
                
                with open("amarin.json", "w", encoding="utf-8") as f:
                    f.write(final_url)
                    
                print(f"✅ Success! URL saved: {final_url}")
            else:
                print("❌ ไม่พบ Request .m3u8 วิ่งผ่านในเครือข่าย")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_data()

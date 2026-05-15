import cloudscraper
import re

def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.amarintv.com/",
    }

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    try:
        response = scraper.get("https://www.amarintv.com/live", headers=headers)

        if response.status_code == 200:
            match = re.search(r'"(https[^"]+\.m3u8[^"]*)"', response.text)
            if match:
                raw_url = match.group(1)

                # --- ส่วนที่แก้ไขเพื่อป้องกัน Error ---
                # 1. ลบเครื่องหมาย \ ที่ปิดท้ายออกก่อน (ถ้ามี) เพื่อป้องกัน unicodeescape error
                clean_raw = raw_url.rstrip('\\')
                
                # 2. แปลง \\u0026 เป็น & (unicode_escape)
                final_url = clean_raw.encode().decode('unicode_escape')
                
                # 3. กวาดล้าง \ ที่อาจหลงเหลืออยู่ในจุดอื่นๆ ออกให้หมด
                final_url = final_url.replace('\\', '')
                
                # 4. ตัดช่องว่างหัวท้ายให้ชัวร์
                final_url = final_url.strip()

                # เขียนลงไฟล์แบบ Plain Text (ไม่ใช้ JSON)
                with open("amarin.json", "w", encoding="utf-8") as f:
                    f.write(final_url)

                print(f"✅ Success! URL saved: {final_url}")
            else:
                print("❌ No M3U8 found.")
        else:
            print(f"❌ Status: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    get_data()

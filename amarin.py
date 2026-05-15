import cloudscraper
import re

def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.amarintv.com/",
    }

    # สร้าง scraper จำลอง Browser
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    try:
        response = scraper.get("https://www.amarintv.com/live", headers=headers)

        if response.status_code == 200:
            # ค้นหา URL .m3u8
            match = re.search(r'"(https[^"]+\.m3u8[^"]*)"', response.text)
            if match:
                raw_url = match.group(1)

                # 1. แปลง \\u0026 ให้เป็น & และจัดการ unicode อื่นๆ
                # 2. ลบ \ ที่ค้างอยู่ออกให้หมด
                final_url = raw_url.encode().decode('unicode_escape').replace('\\', '')
                
                # ลบเครื่องหมาย \ หรือช่องว่างที่หัวท้ายถ้ายังมีเหลือ
                final_url = final_url.strip()

                # เขียนลงไฟล์เป็นข้อความตรงๆ ไม่ใช้ json.dump
                with open("amarin.json", "w", encoding="utf-8") as f:
                    f.write(final_url)

                print(f"✅ Success! URL saved to amarin.json")
                print(f"🔗 URL: {final_url}")
            else:
                print("❌ No M3U8 source found in the page.")
        else:
            print(f"❌ Failed! Status code: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    get_data()

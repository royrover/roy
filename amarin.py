import cloudscraper
import re
import json


def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.amarintv.com/",
    }

    # สร้าง scraper ที่จำลอง Chrome บน Windows
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

                try:
                    # เติมคำพูดครอบเพื่อให้เป็น JSON String ที่สมบูรณ์ แล้วโหลดเข้าไป
                    final_url = json.loads(f'"{raw_url}"')
                except:
                    # หากวิธีแรกพลาด ให้ใช้การลบตัวอักษร \ ที่ค้างอยู่ออกตรงๆ
                    final_url = (
                        raw_url.encode()
                        .decode("unicode_escape", errors="ignore")
                        .replace("\\", "")
                    )

                # แถม: ลบเครื่องหมาย \ ที่อาจจะหลงเหลืออยู่ตัวสุดท้ายออก (ถ้ามี)
                final_url = final_url.strip("\\")

                # เซฟเป็น JSON เพื่อให้ PHP อ่านง่าย
                data = final_url
                with open("amarin.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

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

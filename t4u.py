import cloudscraper
import re

def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://true4u.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

    # สร้าง scraper ที่จำลอง Browser จริง
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    
    try:
        # 1. ยิง API เพื่อเอา URL ที่ผ่านการ Sign แล้ว
        response = scraper.get("https://true4u.com/live-api/signer-url?prefix=/live/", headers=headers)
        
        if response.status_code == 200:
            raw_url = response.text # ค่าที่ได้จะเป็น URL เต็มๆ
            
            # 2. แปลงจาก Master Playlist เป็น 720p ทันที
            # ใช้ raw_url แทน res1 เพราะ res1 เป็น Object ของ Response
            final_url = re.sub("playlist.m3u8", "pl_720p/index.m3u8", raw_url)
            
            # 3. เซฟลงไฟล์ data.json (เขียนทับค่าเดิม)
            with open("data.json", "w", encoding="utf-8") as f:
                f.write(final_url)
                
            print(f"Success! URL saved to data.json")
            print(f"URL: {final_url}")
        else:
            print(f"Failed with status code: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_data()

import cloudscraper
import re

def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36",
        "Referer": "https://true4u.com/",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "th,en;q=0.9"
    }

    # สร้าง Session ผ่าน cloudscraper (ช่วยเก็บบันทึก Cookie และจัดการการเชื่อมต่ออัตโนมัติ)
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    
    try:
        # (ทางเลือก) แวะเข้าหน้าแรกก่อน เพื่อรับคุกกี้เริ่มต้นจาก Cloudflare เหมือนผู้ใช้จริง
        print("กำลังเชื่อมต่อหน้าแรกเพื่อรับ Session และ Cookie...")
        home_response = scraper.get("https://true4u.com/", headers=headers)
        print(f"หน้าแรก Status: {home_response.status_code}")

        # หน่วงเวลาเล็กน้อยหรือยิง API ต่อเนื่องโดยใช้ session เดิม
        print("กำลังดึง API signer-url...")
        response = scraper.get("https://true4u.com/live-api/signer-url?prefix=/live/", headers=headers)
        
        if response.status_code == 200:
            raw_url = response.text # ค่าที่ได้จะเป็น URL เต็มๆ
            
            # แปลงจาก Master Playlist เป็น 720p ทันที
            final_url = re.sub(r"playlist\.m3u8", "pl_720p/index.m3u8", raw_url)
            
            # เซฟลงไฟล์ data.json (เขียนทับค่าเดิม)
            with open("data.json", "w", encoding="utf-8") as f:
                f.write(final_url)
                
            print(f"Success! URL saved to data.json")
            print(f"URL: {final_url}")
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_data()

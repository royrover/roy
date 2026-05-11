import cloudscraper
import json
import os

def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://true4u.com/",
    }

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    
    try:
        res = scraper.get("https://true4u.com/live-api/signer-url?prefix=/live/", headers=headers)
        # เซฟเป็นไฟล์ JSON
        with open("data.json", "w", encoding="utf-8") as f:
            f.write(res.text)
        print("Data saved successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_data()

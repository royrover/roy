import requests
from bs4 import BeautifulSoup
import urllib3
import time
import json
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def convert_time_plus_7(time_str):
    """ฟังก์ชันสำหรับคำนวณบวกเวลาเพิ่ม 7 ชั่วโมง"""
    try:
        time_obj = datetime.strptime(time_str.strip(), "%H:%M")
        new_time = time_obj + timedelta(hours=7)
        return new_time.strftime("%H:%M")
    except Exception:
        return time_str


def get_schedule_api_json():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
            "Connection": "keep-alive",
        }
    )

    json_output = {}

    try:
        # ดึงหน้าแรกดัก Session Bypass
        url = "https://dlhd.st/index.php"
        response = session.get(url, timeout=15, verify=False)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        return json.dumps({"error": f"Connection failed: {str(e)}"}, ensure_ascii=False)

    soup = BeautifulSoup(html_content, "html.parser")
    days = soup.find_all("div", class_="schedule__day")

    for day in days:
        day_title_el = day.find("div", class_="schedule__dayTitle")
        day_title = (
            day_title_el.get_text(strip=True) if day_title_el else "Unknown Date"
        )

        if day_title not in json_output:
            json_output[day_title] = {}

        categories = day.find_all("div", class_="schedule__category")
        for cat in categories:
            cat_header_el = cat.find("div", class_="card__meta")
            cat_name = (
                cat_header_el.get_text(strip=True) if cat_header_el else "General"
            )

            if cat_name not in json_output[day_title]:
                json_output[day_title][cat_name] = []

            events = cat.find_all("div", class_="schedule__event")
            for event in events:
                time_el = event.find("span", class_="schedule__time")
                raw_time = time_el.get_text(strip=True) if time_el else "00:00"
                th_time = convert_time_plus_7(raw_time)

                title_el = event.find("span", class_="schedule__eventTitle")
                event_title = title_el.get_text(strip=True) if title_el else "No Title"

                # ดึงช่องสตรีมและเก็บค่าโครงสร้างย่อย (channel_name, channel_id) ตามรูปภาพ
                channels_list = []
                channels_div = event.find("div", class_="schedule__channels")
                if channels_div:
                    channel_links = channels_div.find_all("a")
                    for ch in channel_links:
                        ch_name = ch.get_text(strip=True)
                        ch_href = ch.get("href", "")

                        # สกัดไอดีช่องจาก parameter ท้ายลิงก์ (เช่น watch.php?id=77 -> 77)
                        ch_id = ""
                        if "id=" in ch_href:
                            ch_id = ch_href.split("id=")[-1]
                        else:
                            ch_id = ch_href.split("/")[-1].replace(".php", "")

                        if ch_id == "00":
                            continue
                        channels_list.append(
                            {"channel_name": ch_name, "channel_id": ch_id}
                        )

                # สร้างโครงสร้างข้อมูลคู่การแข่งขันตรงตามฟอร์แมตในรูปภาพเป๊ะๆ (ไม่มี channels2)
                event_data = {
                    "time": th_time,
                    "event": event_title,
                    "channels": channels_list,
                }
                json_output[day_title][cat_name].append(event_data)

    # ส่งกลับค่าเป็น API JSON String
    return json.dumps(json_output, ensure_ascii=False)


if __name__ == "__main__":
    # เรียกใช้ฟังก์ชันรับข้อมูล API JSON ตรงๆ
    api_json = get_schedule_api_json()
    output_file = "daddylive_schedule.json"

    if "error" in api_json:
        print(f"❌ ระบบขัดข้อง: {api_json}")
    else:
        # บันทึกข้อมูล JSON ลงในไฟล์
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(api_json)
        print(f"💾 บันทึกตารางการแข่งขันลงไฟล์ {output_file} เรียบร้อยแล้ว!\n")

        # พิมพ์ออกแบบ Pretty-print แสดงผลเหมือนบนหน้าจอรูปภาพของคุณ
        parsed_clean = json.loads(api_json)
        print(json.dumps(parsed_clean, ensure_ascii=False, indent=4))

import json
import re
import time
import requests
from bs4 import BeautifulSoup

# 1. กำหนด Headers เพื่อเลียนแบบเบราว์เซอร์มนุษย์ ป้องกันเซิร์ฟเวอร์บล็อก Request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. สร้างเลข Timestamp เพื่อเคลียร์แคช (Cache Buster)
cache_buster = int(time.time() * 1000)
url = f"https://embed-xs.bananacake.org/dooball66v2/schedule.html?v={cache_buster}"

print(f"📡 กำลังดึงข้อมูลจากเว็บ... (v={cache_buster})")

try:
    response = requests.get(url, headers=headers, timeout=15)
    html_content = response.text
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลเว็บ: {e}")
    html_content = ""


def fix_thai_encoding(text):
    """แก้ไขปัญหาข้อความภาษาไทยกลายเป็นอักษรต่างดาว (Latin1 -> UTF-8)"""
    if not text:
        return ""
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


def keep_only_english(text):
    """ลบภาษาไทยออกทั้งหมดเพื่อให้เหลือเฉพาะภาษาอังกฤษ ตัวเลข และสัญลักษณ์สากล"""
    if not text:
        return ""
    # ใช้ Regex คัดเฉพาะตัวอักษรภาษาอังกฤษ ตัวเลข ช่องว่าง และสัญลักษณ์ทั่วไป
    eng_parts = re.findall(r"[A-Za-z0-9\s\-\.\'\(\)]+", text)
    clean_text = " ".join(eng_parts).strip()
    # ลดช่องว่างที่อาจจะเบิ้ลซ้ำกันให้เหลือช่องเดียว
    clean_text = re.sub(r"\s+", " ", clean_text)
    return clean_text


def clean_time_string(time_str):
    """แยกแยะระหว่างเวลาปกติ (เช่น 10:30) และ วันที่พร้อมเวลา (เช่น 20/05 12:00)"""
    time_str = time_str.strip() if time_str else ""
    if not time_str:
        return {"date": "", "time": ""}

    parts = time_str.split()
    if len(parts) > 1:
        return {"date": parts[0], "time": parts[1]}
    return {"date": "", "time": parts[0]}


def extract_matches_pool(html):
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    matches_pool = []

    # หาบล็อกกีฬาทั้งหมด (.sport-wrapper)
    wrappers = soup.select(".sport-wrapper")

    for wrapper in wrappers:
        # 🟢 ดึงชื่อคลาสเก็บเข้าตัวแปร sport_type
        classes = wrapper.get("class", [])
        sport_type = classes[1] if len(classes) > 1 else "Unknown"

        # 🔥 ตรงเป๊ะตามบรีฟ: ข้ามลูป "เฉพาะ" คลาสที่เป็นกราฟิก Soccer-VM เท่านั้น (คลาส Soccer ปกติปล่อยผ่าน)
        if "Soccer-VM" in sport_type:
            continue

        # แกะชื่อรายการ/ลีก (รองรับทั้งแบบ Live และ Upcoming)
        header_el = wrapper.select_one(".match-live-header") or wrapper.select_one(
            ".match-upcoming-header"
        )
        league = header_el.get_text(strip=True) if header_el else ""
        league = fix_thai_encoding(league)

        # ตัดคำนำหน้าประเภทกีฬาออกเพื่อให้ชื่อลีกสะอาด
        if ": " in league:
            league = league.split(": ", 1)[-1]

        # ค้นหาแถวแมตช์ทั้งหมด (เอาทุกคู่ในลีกนั้น)
        match_rows = wrapper.select(".match")

        for match_row in match_rows:
            # แกะ Match ID จาก attribute onclick
            match_id = ""
            onclick_div = match_row.find(lambda tag: tag.has_attr("onclick"))
            if onclick_div:
                onclick_text = onclick_div["onclick"]
                match_id_search = re.search(r"'(.*?)'", onclick_text)
                if match_id_search:
                    match_id = match_id_search.group(1)

            # แกะเวลาและเช็คสถานะ Live
            time_node = match_row.select_one(".justify-content-left")
            raw_time = time_node.get_text(strip=True) if time_node else ""

            is_live = "match-live" in match_row.get("class", [])
            live_time = ""
            if is_live and time_node and time_node.select_one(".live_blink"):
                live_time = time_node.select_one(".live_blink").get_text(strip=True)
                raw_time = (
                    time_node.contents[0].strip() if time_node.contents else raw_time
                )

            time_info = clean_time_string(raw_time)

            # เช็คประเภทแมตช์ (เดี่ยว หรือ ทีม)
            single_title_el = match_row.select_one(
                ".text-center"
            ) or match_row.select_one(".text-left")
            is_single = (
                single_title_el is not None
                and "panel-title" not in single_title_el.get("class", [])
            )

            match_data = {
                "match_id": match_id,
                "sport_type": sport_type,
                "league": league,
                "date": time_info["date"],
                "time": time_info["time"],
                "live_time": live_time,
                "is_live": is_live,
                "is_single_event": is_single,
                "title": "",
                "home_team": "",
                "away_team": "",
                "score_or_vs": "vs",
            }

            if is_single:
                title_text = single_title_el.get_text(strip=True)
                # คลีนชื่อรายการเดี่ยวให้เป็นอังกฤษล้วน
                match_data["title"] = keep_only_english(fix_thai_encoding(title_text))
            else:
                home_el = match_row.select_one(".justify-content-end.text-right")
                score_el = match_row.select_one(
                    ".col-1.flex-wrap.justify-content-center"
                )
                away_el = match_row.select_one(
                    ".justify-content-start.align-items-center span"
                ) or match_row.select_one(".justify-content-start span")

                home_text = home_el.get_text(" ", strip=True) if home_el else ""
                away_text = away_el.get_text(" ", strip=True) if away_el else ""

                # ✨ คลีนภาษาไทยปนออก เหลือเฉพาะชื่อทีมภาษาอังกฤษภาษาเดียวตามที่คุณสั่ง
                match_data["home_team"] = keep_only_english(
                    fix_thai_encoding(home_text.split("\n")[0])
                )
                match_data["away_team"] = keep_only_english(
                    fix_thai_encoding(away_text.split("\n")[0])
                )
                match_data["score_or_vs"] = (
                    score_el.get_text(strip=True) if score_el else "vs"
                )

            if match_id:
                matches_pool.append(match_data)

    return matches_pool


# เริ่มทำงานแกะข้อมูล
extracted_data = extract_matches_pool(html_content)

# บันทึกข้อมูลลงไฟล์ JSON
with open("matches_pool.json", "w", encoding="utf-8") as f:
    json.dump(extracted_data, f, ensure_ascii=False, indent=4)

print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
print(
    f"\n🎯 บันทึกสำเร็จ! ข้ามเฉพาะ Soccer-VM และคลีนชื่อทีมภาษาอังกฤษล้วนเรียบร้อยครับ"
)

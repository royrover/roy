import datetime
import re
import json
import urllib.request
import os
import sys

SPORTSONLINE = os.getenv("SPORTSONLINE")

def main():
    url = SPORTSONLINE
    if not url:
        print("❌ ไม่พบแปรสภาพแวดล้อม SPORTSONLINE (Environment Variable)")
        sys.exit(1)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        },
    )

    try:
        # กำหนด timeout เผื่อเน็ตเวิร์กของ GitHub Actions หน่วง
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
        sys.exit(1)

    # ปรับจุดที่ 1: ใช้ splitlines() เพื่อจัดการปัญหา \r\n (CRLF) บน Linux GitHub Actions
    lines = [line.strip() for line in html.splitlines() if line.strip()]

    # 1. แผนผังวันที่ระบบ (หาจุดตั้งต้นจากวันปัจจุบัน)
    file_days = [
        line.upper() for line in lines if re.match(r"^[A-Z]+DAY$", line.upper())
    ]
    
    # 💡 บน GitHub Actions ตัวเซิร์ฟเวอร์จะเป็นเวลา UTC เสมอ 
    # แต่เนื่องจากลอจิกใช้คำนวณหา index ของวันในสัปดาห์ (weekday) ความเสี่ยงจึงต่ำ 
    # ยกเว้นช่วงรอยต่อเวลา 00:00 น. แนะนำให้ใช้เวลาปัจจุบันของระบบเป็นตัวตั้ง
    today_name = datetime.datetime.now().strftime("%A").upper()
    today_date = datetime.datetime.now()

    day_dates_map = {}
    try:
        found_today_idx = file_days.index(today_name)
    except ValueError:
        found_today_idx = 0

    for idx, fd in enumerate(file_days):
        offset = idx - found_today_idx
        calc_date = today_date + datetime.timedelta(days=offset)
        day_dates_map[fd] = calc_date.strftime("%d-%m-%Y")

    current_day_name = None
    grouped_by_date = {}
    last_hour = -1
    day_offset = 0

    # 2. ลูปสกัดข้อมูล
    for line in lines:
        if re.match(r"^[A-Z]+DAY$", line.upper()):
            current_day_name = line.upper()
            last_hour = -1
            day_offset = 0
            continue

        if any(
            k in line.upper()
            for k in [
                "NEW DOMAIN",
                "IMPORTANT!",
                "READ!",
                "24/7 CHANNELS",
                "INFO:",
                "EMAIL:",
            ]
        ):
            continue

        # ปรับจุดที่ 2: แก้ไขโครงสร้างดีเทลเพื่อรองรับการเว้นวรรคไม่สม่ำเสมอตรงเครื่องหมาย |
        match = re.match(r"^(\d{2}:\d{2})\s+([^|]+?)(?:\s*\|\s*(https?://\S+))?$", line)
        if match:
            if not current_day_name or current_day_name not in day_dates_map:
                continue

            orig_time = match.group(1)
            raw_title = match.group(2).strip()
            station_url = match.group(3).strip() if match.group(3) else ""

            if (
                re.match(
                    r"^(HD\d+|BR\d+|SPORTS|ENGLISH|SPANISH|GERMAN)",
                    raw_title,
                    re.IGNORECASE,
                )
                and not station_url
            ):
                continue

            current_hour = int(orig_time.split(":")[0])

            # ลอจิกชั่วโมงย้อนศรคุมทิศทางวันข้ามคืน (คงไว้ตามโครงสร้างเดิมของคุณ)
            if last_hour != -1 and current_hour < last_hour:
                day_offset += 1

            last_hour = current_hour

            # ดึงวันที่ตามปฏิทินเว็บ
            base_date_str = day_dates_map[current_day_name]
            base_dt = datetime.datetime.strptime(base_date_str, "%d-%m-%Y")
            base_dt = base_dt + datetime.timedelta(days=day_offset)

            # มัดรวมก้อนเวลาเดิม ➔ แล้วสั่งบวกเวลาไทยล่วงหน้า +6 ชั่วโมง
            raw_datetime_str = f"{base_dt.strftime('%d-%m-%Y')} {orig_time}"

            try:
                dt_obj = datetime.datetime.strptime(raw_datetime_str, "%d-%m-%Y %H:%M")
                dt_th = dt_obj + datetime.timedelta(hours=6)

                th_date = dt_th.strftime("%Y-%m-%d")
                th_time = dt_th.strftime("%H:%M")
            except Exception:
                th_date = base_dt.strftime("%Y-%m-%d")
                th_time = orig_time

            if th_date not in grouped_by_date:
                grouped_by_date[th_date] = {}

            # ใช้ "เวลา + ชื่อคู่" เป็นตัวยุบรวมลิงก์ในวันนั้น ๆ
            match_key = f"{th_time}_{raw_title}"

            if match_key not in grouped_by_date[th_date]:
                grouped_by_date[th_date][match_key] = {
                    "time": th_time,
                    "title": raw_title,
                    "urls": [],
                }

            if (
                station_url
                and station_url not in grouped_by_date[th_date][match_key]["urls"]
            ):
                grouped_by_date[th_date][match_key]["urls"].append(station_url)

    # 3. จัดโครงสร้างข้อมูลให้เรียงลำดับเวลา (Sort)
    final_groups = []

    for date_key in sorted(grouped_by_date.keys()):
        sorted_matches = list(grouped_by_date[date_key].values())
        sorted_matches.sort(key=lambda x: x["time"])

        final_groups.append({"date": date_key, "matches": sorted_matches})

    output_data = {"groups": final_groups}

    # พ่นออกเป็นไฟล์สากล API
    with open("sportsonline_api.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("✅ บันทึกไฟล์สำเร็จ! จำนวนกลุ่มวันที่จับคู่ได้:", len(final_groups))


if __name__ == "__main__":
    main()

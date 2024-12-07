import re
import requests
import json
from datetime import datetime, timedelta

# URL of the text file
url = "https://sportsonline.gl/prog.txt"

# Fetch the content of the text file
response = requests.get(url)
if response.status_code != 200:
    print("Failed to fetch the content from the URL.")
    exit()

# Searching for time pattern in the content of the file
matches = re.findall(r"(\d{2}:\d{2}.{3}.*?) \| (http.*?\.php)", response.text)

# Get today's date in the required format
today_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Template for the final JSON structure
data = {
    "name": "sportsonline.gl",
    "image": "https://static.thairath.co.th/media/dFQROr7oWzulq5Fa5LJEXNHgK8Nkou0mFfNIBOUFttbzB1Odu55E3VaV0f8gNyuUy8L.jpg",
    "url": "https://dl.dropbox.com/scl/fi/04bcea7wnj2tea0bbqtuj/SPORT.w3u?rlkey=fogj7jaec08k2klrxjl8xdn3h&st=ho0u09uh&dl=0",
    "author": f"royrover update {today_date}",
    "stations": []
}

# Populate the "stations" list with extracted matches
image_url = "https://static.thairath.co.th/media/dFQROr7oWzulq5Fa5LJEXNHgK8Nkou0mFfNIBOUFttbzB1Odu55E3VaV0f8gNyuUy8L.jpg"
referer = "https://sportsonline.gl"

for match in matches:
    event_name, event_url = match
    # Extract and add 6 hours to the time in event_name
    time_match = re.match(r"(\d{2}:\d{2})", event_name)
    if time_match:
        original_time = datetime.strptime(time_match.group(1), "%H:%M")
        updated_time = original_time + timedelta(hours=6)
        event_name = event_name.replace(time_match.group(1), updated_time.strftime("%H:%M"))

    # Append the event to the stations list
    data["stations"].append({
        "name": event_name.strip(),
        "image": image_url,
        "url": event_url,
        "isHost": "true",
        "referer": referer
    })

# Write the JSON data to SPORT.w3u file
with open("SPORT.w3u", "w") as file:
    file.write(json.dumps(data, indent=4))

print("File SPORT.w3u created successfully.")

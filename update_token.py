import os
import requests
from playwright.sync_api import sync_playwright

# ตั้งค่า Cloudflare API สำหรับอัปเดต KV
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_KV_NAMESPACE_ID = os.environ.get("CF_KV_NAMESPACE_ID")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN")

def update_cloudflare_kv(stream_url):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/GMM25_STREAM_URL"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "text/plain"
    }
    response = requests.put(url, headers=headers, data=stream_url)
    if response.status_code == 200:
        print("Successfully updated stream URL to Cloudflare KV!")
    else:
        print(f"Failed to update KV: {response.text}")

def run():
    captured_url = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # ดักจับ Network Request เพื่อหาลิงก์ .m3u8 ของ Fastly
        def handle_request(route, request):
            nonlocal captured_url
            if "fastly.live.brightcove.com" in request.url and ".m3u8" in request.url:
                if not captured_url:
                    captured_url = request.url
                    print(f"Captured Stream URL: {captured_url}")
            route.continue_()

        page.route("**/*", handle_request)

        print("Navigating to oned.net...")
        try:
            page.goto("https://www.oned.net/live-tv/gmm25", timeout=60000)
            # รอให้เครื่องเล่นโหลดและยิงสตรีม (ประมาณ 10-15 วินาที)
            page.wait_for_timeout(15000)
        except Exception as e:
            print(f"Error loading page: {e}")
        
        browser.close()

    if captured_url:
        update_cloudflare_kv(captured_url)
    else:
        raise Exception("Could not capture the stream URL!")

if __name__ == "__main__":
    run()

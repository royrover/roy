import json
import os
from playwright.sync_api import sync_playwright

def run():
    captured_url = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

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
            page.wait_for_timeout(15000)
        except Exception as e:
            print(f"Error loading page: {e}")
        
        browser.close()

    if captured_url:
        data = {"stream_url": captured_url}
        # เซฟเป็นไฟล์ gmm25.json ให้ตรงกับ Workflow
        with open("gmm25.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Updated gmm25.json successfully!")
    else:
        raise Exception("Could not capture the stream URL!")

if __name__ == "__main__":
    run()

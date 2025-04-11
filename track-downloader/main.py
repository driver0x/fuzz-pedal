import os
import random
import urllib.request
from patchright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        with p.chromium.launch_persistent_context(
            user_data_dir="browser", 
            channel="chrome",
            headless=True, 
            no_viewport=True
            ) as browser:
            page = browser.pages[0]
            page.set_default_navigation_timeout(0)
            page.set_default_timeout(0)
            track_url = input("Download track? ")
            page.goto(track_url, wait_until="networkidle")
            with page.expect_request(lambda request: "https://static.bandlab.com/revisions-formatted" in request.url) as request_info:
                page.locator("player-audio-button").first.click()
            m4a_url = request_info.value.url
            m4a_path = f"{os.path.dirname(os.path.realpath(__file__))}/{random.randint(0, 10000)}.m4a"
            urllib.request.urlretrieve(m4a_url, m4a_path)
            print(m4a_path)

if __name__ == "__main__":
    main()
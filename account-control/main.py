import re
import json
import base64
import time
from patchright.sync_api import sync_playwright
from pymailtm import Account

def main():
    accounts = input("Path to accounts.txt? ")
    with open(accounts, "r") as file:
        lines = file.readlines()
    accounts_len = len(lines)
    i = int(input("Start at line? "))
    i -= 1
    print(f"Controlling {accounts_len} accounts.")
    while i < accounts_len:
        print(f"{i+1} of {accounts_len}: Loading account information...")
        info = lines[i].split(":")
        email = Account(info[2], info[0], info[1])
        cookies = None
        try:
            cookies = json.loads(base64.b64decode(info[3]).decode())
        except:
            pass
        print(f"{i+1} of {accounts_len}: Starting headless chrome...")
        with sync_playwright() as p:
            with p.chromium.launch_persistent_context(
                user_data_dir="browser", 
                channel="chrome",
                headless=True, 
                no_viewport=True
                ) as browser:
                browser.clear_cookies() # Clear old cookies
                if cookies != None:
                    print(f"{i+1} of {accounts_len}: Loading cookies...")
                    browser.add_cookies(cookies)
                page = browser.pages[0]
                page.set_default_navigation_timeout(0)
                page.set_default_timeout(0)
                page.goto('https://www.bandlab.com/login', wait_until="networkidle")
                if page.get_by_text("Log in").is_visible():
                    print(f"{i+1} of {accounts_len}: Completing login...")
                    old_messages_id = email._get_existing_messages_id() # Get old emails
                    page.get_by_placeholder("Username or email").fill(info[0])
                    page.get_by_placeholder("Enter at least 6 characters").fill(info[1])
                    page.get_by_role("button", name="Log in").click()
                    print(f"{i+1} of {accounts_len}: Waiting for 2FA email...")
                    email_text = None
                    while True:
                        try: # Wait for new email to be received
                            new_messages = list(filter(lambda m: m.id_ not in old_messages_id, email.get_messages()))
                            if new_messages:
                                email_text = new_messages[0].text
                                break
                        except:
                            time.sleep(2)
                            continue
                    print(f"{i+1} of {accounts_len}: Completing 2FA...")
                    code = re.search(r'Your verification code is \*(.*?)\*\.', email_text).group(1) # Regex verification code
                    page.locator(".input-big-letter").first.fill(code)
                    page.get_by_role("button", name="Next").click()
                    page.wait_for_url("https://www.bandlab.com/feed/trending")
                    print(f"{i+1} of {accounts_len}: Writing new cookie to account.txt...")
                    cookies = base64.b64encode(json.dumps(browser.cookies("https://www.bandlab.com")).encode()).decode()
                    lines[i] = f"{info[0]}:{info[1]}:{info[2]}:{cookies}\n"
                    with open(accounts, "w") as file:
                        file.writelines(lines)
                    print(f"{i+1} of {accounts_len}: Login process finished.")

                # Do whatever you want here
        i += 1
        time.sleep(1) # Prevent bandlab from dying

if __name__ == "__main__":
    main()
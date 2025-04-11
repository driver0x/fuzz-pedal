import time
import json
import base64
from bs4 import BeautifulSoup
from patchright.sync_api import sync_playwright, Page
from pymailtm import MailTm, Account

antcpt_api_key = ""
client = MailTm()

def verify_email(email: Account) -> str:
    email_html = None
    messages = None
    while True: 
        messages = email.get_messages()
        if (len(messages) >= 2): # Wait for 2 or more messages to be received
            break
        time.sleep(3)
    for i in range(len(messages)):
        if "please confirm your email address" in messages[i].subject: # Find confirmation email
            email_html = str(messages[i].html)
            break
    soup = BeautifulSoup(email_html, features="html.parser") # Parse email HTML
    verify_link = None
    links = soup.select('a[style="background-color:#f12c18; border:0px solid #f12c18; border-color:#f12c18; border-radius:50px; border-width:0px; color:#ffffff; display:inline-block; font-size:16px; font-weight:bold; letter-spacing:0px; line-height:normal; padding:10px 20px 10px 20px; text-align:center; text-decoration:none; border-style:solid; font-family:helvetica,sans-serif;"]')
    for link in links:
        verify_link = link.get("href")
    return verify_link

def solve_captcha(page: Page):
    code = """var d = document.getElementById("anticaptcha-imacros-account-key");
    if (!d) {
        d = document.createElement("div");
        d.innerHTML = "API_KEY";
        d.style.display = "none";
        d.id = "anticaptcha-imacros-account-key";
        document.body.appendChild(d);
    }
"""
    page.evaluate(code.replace("API_KEY", antcpt_api_key))
    page.add_script_tag(url="https://cdn.antcpt.com/imacros_inclusion/recaptcha.js")

def generate_account(name: str, password: str, talents: list[str], genres: list[str], artists: list[str], username: str = None, profile_pic: str = None) -> str:
    print("Generating email...")
    email = None
    while True:
        try:
            email = client.get_account(password)
        except:
            print("mail.tm API failed, retrying in 3 seconds...")
            time.sleep(3)
            continue
        break
    print("Starting headless chrome...")
    with sync_playwright() as p:
        with p.chromium.launch_persistent_context(
            user_data_dir="browser", 
            channel="chrome", 
            headless=True, 
            no_viewport=True
            ) as browser:
            browser.clear_cookies() # Clear old cookies
            page = browser.pages[0]
            page.set_default_navigation_timeout(0)
            page.set_default_timeout(0)
            print("Injecting catpcha solver...")
            page.on("load", solve_captcha) # Load captcha solving script
            print("Completing sign up page...")
            page.goto('https://www.bandlab.com/sign-up', wait_until="networkidle")
            page.get_by_placeholder("Enter your name").fill(name) # Name
            page.get_by_placeholder("you@example.com").fill(email.address) # Email
            page.get_by_placeholder("Enter at least 6 characters").fill(password) # Password
            page.locator("select[ng-model='pickDate.day']").select_option("1") # Day
            page.locator("select[ng-model='pickDate.month']").select_option("1") # Month
            page.locator("select[ng-model='pickDate.year']").select_option("2000") # Year
            page.get_by_role("button", name="Sign up").click()
            print("Completing sign up captcha...")
            # Attempt to close captcha pop up (ass method)
            for i in range(10):
                page.mouse.click(10, 10)
                time.sleep(0.3)
            page.wait_for_url("https://www.bandlab.com/onboarding")

            print("Completing onboarding page...")
            if profile_pic != None:
                print("Uploading profile picture...")
                page.locator("div[class='quick-upload-cover-cta form-field-upload-picture-img-circle']").click()
                page.locator("input[type='file']").set_input_files(profile_pic)
                page.get_by_role("button").get_by_text("Upload Picture").click() # Upload profile picture
                print("Profile picture uploaded.")
            if (username != None):
                page.get_by_placeholder("Set a custom username").fill(username) # Username
            page.get_by_role("button", name="Continue").click()
            page.wait_for_selector("div[class='complete-profile-goals']")
            page.get_by_role("button", name="Continue").click()
            t_element = page.get_by_label("Tell Us More About You") # Talents
            for t in talents:
                try:
                    t_element.get_by_text(t).click()
                except:
                    print(f"No talent found for: {t}")
            page.get_by_role("button", name="Continue").click()
            g_element = page.get_by_label("Pick Your Favorite Genres") # Favourite genres
            for g in genres:
                try:
                    g_element.get_by_text(g).click()
                except:
                    print(f"No genre found for: {t}")
            page.get_by_role("button", name="Continue").click()
            for a in artists: # Search and select inspired-by artists
                page.get_by_placeholder("Search Artists…").fill(a)
                page.locator("div[class='mentions-suggestions-fullname']").filter(has_text=a).nth(1).click()
            page.get_by_role("button", name="Done").click()
            page.wait_for_url("https://www.bandlab.com/feed/trending") # Wait for sign up to finish

            print("Waiting for verification email...")
            verify_link = verify_email(email)
            page.goto(verify_link, wait_until="networkidle")
            print("Completing email verification...")
            page.wait_for_url("https://www.bandlab.com/feed/trending") # Wait for verification redirect
            cookies = base64.b64encode(json.dumps(browser.cookies("https://www.bandlab.com")).encode()).decode()
    return (email.address, email.id_, cookies)
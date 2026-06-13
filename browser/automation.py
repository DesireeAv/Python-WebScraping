"""
Part 1 — Browser automation via Playwright.

Logs in as the test user, completes MFA, updates banking and payment
details on /app/account, then verifies the summary reflects the saved data.
"""

import os
import logging

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
load_dotenv()

from browser.pages.login_page import LoginPage
from browser.pages.mfa_page import MFAPage
from browser.pages.account_page import AccountPage
from browser.data.test_data import (
    BANK_ROUTING,
    BANK_ACCOUNT,
    CARD_NAME,
    CARD_NUMBER,
    CARD_EXPIRY,
    CARD_CVC,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

BASE_URL = "https://challenge.onsetto.dev/login"


def run(headless: bool = False) -> None:
    email = os.environ["EMAIL"]
    password = os.environ["PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            log.info("Navigating to %s", BASE_URL)
            page.goto(BASE_URL)

            #page.pause()

            log.info("Logging in as %s", email)
            LoginPage(page).login(email, password)

            log.info("Completing MFA")
            MFAPage(page).verify("1234")
            
            print("Current URL:", page.url)

            page.wait_for_timeout(2000)

            elements = page.locator("[id]")

            count = elements.count()

            print(f"Found {count} IDs")

            for i in range(count):
                print(elements.nth(i).get_attribute("id"))


            log.info("Navigating to account page")
            page.goto(f"https://marketplace.dev-challenge.com/app/account")
            page.wait_for_load_state("networkidle")

            account = AccountPage(page)

            log.info("Updating banking details (routing=***%s)", BANK_ROUTING[-4:])
            account.update_banking(BANK_ROUTING, BANK_ACCOUNT)

            log.info("Updating payment details (card=***%s)", CARD_NUMBER[-4:])
            account.update_payment(CARD_NAME, CARD_NUMBER, CARD_EXPIRY, CARD_CVC)

            log.info("Verifying summary")
            account.verify_summary(BANK_ROUTING, BANK_ACCOUNT, CARD_NUMBER, CARD_EXPIRY)

            log.info("Part 1 complete — browser automation succeeded")

        except Exception:
            log.exception("Automation failed")
            page.screenshot(path="error_screenshot.png")
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    run()

"""
Part 2 — Python API client.

"""

from __future__ import annotations

import json
import logging
import os
import sys

from dotenv import load_dotenv

from api import APIClient, AuthService, AccountService
from api.exceptions import ChallengeAPIError
from browser.data.test_data import (
    BANK_ROUTING,
    BANK_ACCOUNT,
    CARD_NAME,
    CARD_NUMBER,
    CARD_EXPIRY,
    CARD_CVC,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

API_BASE_URL = "https://zvyhufnwclhcvmgtqxwp.supabase.co/functions/v1/api-v1"
MFA_CODE = "1234" 


def _pretty(label: str, data: dict) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {label}")
    print(f"{'─' * 50}")
    print(json.dumps(data, indent=2))


def run() -> int:
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if not username or not password:
        log.error("USERNAME and PASSWORD must be set (see .env.example)")
        return 1

    client = APIClient(API_BASE_URL)
    auth = AuthService(client)
    account = AccountService(client)

    try:
        # Step 1 — login
        log.info("Logging in as %s", username)
        login_resp = auth.login(username, password)
        mfa_token = login_resp["mfa_token"]

        # Step 2 — MFA
        log.info("Verifying MFA")
        auth.verify_mfa(mfa_token, MFA_CODE)
        log.info("Authenticated")

        # Step 3 — banking update
        log.info("Updating banking details")
        banking_conf = account.update_banking(BANK_ROUTING, BANK_ACCOUNT)
        _pretty("Banking confirmation (masked)", banking_conf)

        # Step 4 — payment update
        log.info("Updating payment details")
        payment_conf = account.update_payment(
            CARD_NAME, CARD_NUMBER, CARD_EXPIRY, CARD_CVC
        )
        _pretty("Payment confirmation (masked)", payment_conf)

        log.info("Part 2 complete — all updates successful")
        return 0

    except ChallengeAPIError as exc:
        log.error("API error: %s", exc)
        return 1
    except KeyError as exc:
        log.error(
            "Unexpected response shape — missing key %s. "
            "Check API docs for schema changes.",
            exc,
        )
        return 1


if __name__ == "__main__":
    sys.exit(run())

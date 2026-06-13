# Onsetto Engineering Challenge

A two-part solution:

- **Part 1** — Playwright browser automation that logs in, completes MFA, updates banking and payment details, and verifies the summary.
- **Part 2** — A pure-Python REST API client that performs the same updates via the published API, printing masked confirmations.

---

## Project structure

```
engineering-challenge/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── api_runner.py          ← Part 2 entry point
│
├── browser/
│   ├── automation.py      ← Part 1 entry point
│   ├── pages/
│   │   ├── login_page.py
│   │   ├── mfa_page.py
│   │   └── account_page.py
│   └── data/
│       └── test_data.py   ← Fake test data only
│
└── api/
    ├── __init__.py
    ├── client.py          ← HTTP client with retry/back-off
    ├── auth.py            ← Login + MFA flow
    ├── account.py         ← Banking + payment updates
    └── exceptions.py      ← Custom exception hierarchy
```

---

## Prerequisites

- Python 3.10+
- `pip` or a virtual-env manager (see optional uv/Poetry notes below)

---

## Installation

```bash
# 1. Clone / unzip the project
cd engineering-challenge

# 2. Create and activate a virtual environment (this is important for newer Ubuntu distros)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binaries (Part 1 only)
playwright install chromium
```

---

## Environment variables

| Variable   | Description                       | Default (sandbox)           |
|------------|-----------------------------------|-----------------------------|
| `USERNAME` | Sandbox account email             | `candidate1@onsetto.test`   |
| `PASSWORD` | Sandbox account password          | `Password123!`              |
| `MFA_CODE` | It accepts whatever               | `123456`                    |

> **Important:** this is a simulation environment. Never substitute real financial or personal data.

---

## Running Part 1 — Browser automation

```bash
python -m browser.automation
```

What it does:
1. Opens a Chromium browser (visible by default; set `headless=True` in `automation.py` for CI).
2. Logs in with `USERNAME` / `PASSWORD`.
3. Completes the MFA step (sandbox accepts any 6-digit code).
4. Navigates to `/app/account`.
5. Submits banking details (9-digit routing, 9-digit account number).
6. Submits payment details (Luhn-valid Visa test card, future expiry).
7. Reads the `#last-updated-summary` element and asserts the masked values are present.
8. Prints `✓ Part 1 complete` on success, or saves `error_screenshot.png` on failure.

---

## Running Part 2 — API client

```bash
python -m api.main
```

What it does:
1. `POST /auth/token` with credentials → receives `mfa_token`.
2. `POST /auth/mfa/verify` with `mfa_token` + code → receives `access_token` (stored on the client).
3. `PUT /account/banking` → prints the masked confirmation JSON.
4. `PUT /account/payment` → prints the masked confirmation JSON.

Sample output:

```
2025-01-01 12:00:00 [INFO] Logging in as candidate1@onsetto.test
2025-01-01 12:00:01 [INFO] Verifying MFA
2025-01-01 12:00:01 [INFO] ✓ Authenticated
2025-01-01 12:00:01 [INFO] Updating banking details

──────────────────────────────────────────────────
  Banking confirmation (masked)
──────────────────────────────────────────────────
{
  "routing_number": "***0021",
  "account_number": "***6789"
}

──────────────────────────────────────────────────
  Payment confirmation (masked)
──────────────────────────────────────────────────
{
  "card_number": "***1111",
  "cardholder_name": "Test User"
}

2025-01-01 12:00:02 [INFO] ✓ Part 2 complete — all updates successful
```

---

## Error handling

| Scenario              | Behaviour                                          |
|-----------------------|----------------------------------------------------|
| Wrong credentials     | `AuthError` with a clear message; exits with code 1 |
| Wrong MFA code        | `MFAError` with a clear message                    |
| Validation failure    | `ValidationError` showing the server detail field  |
| Rate limit (429)      | Logged warning; PUT requests auto-retry with exponential back-off (max 3 retries, capped at 30 s) |
| Server error (5xx)    | `AccountUpdateError`; stack trace visible at DEBUG level |
| Browser automation failure | Screenshot saved to `error_screenshot.png`   |

---

# Testing

```bash
pytest --cov=api
```
# Python-WebScraping
# Python-WebScraping

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
├── api/
|   ├── __init__.py
|   ├── client.py          ← HTTP client with retry/back-off
|   ├── auth.py            ← Login + MFA flow
|   ├── account.py         ← Banking + payment updates
|   └── exceptions.py      ← Custom exception hierarchy
|
└── tests/
    ├── test_account.py    
    ├── test_auth.py       
    └── test_client.py      
    
```
## Design Decisions

### Browser Automation
The Playwright implementation follows the Page Object Model (POM) pattern:

- `LoginPage` handles authentication.
- `MFAPage` handles MFA verification.
- `AccountPage` handles banking and payment updates.

This separation keeps selectors isolated from business logic and improves maintainability.

### API Client
The API implementation is separated into service layers:

- `APIClient` manages HTTP requests and authentication state.
- `AuthService` handles login and MFA token exchange.
- `AccountService` handles banking and payment updates.

Custom exception types provide consistent error handling across all API operations.

### Test Data
Only sandbox/test data is used. No real banking or payment information is required.

---

## Prerequisites
- Linux (Debian based distro)
- Python 3.10+
- `pip` or a virtual-env manager

---

## Installation

```bash
# 1. Clone / unzip the project
cd Python-WebScraping

# 2. Create and activate a virtual environment (this is important for newer Ubuntu distros)
python -m venv .venv
source .venv/bin/activate   

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binaries (Part 1 only)
playwright install chromium
```

---

## Environment variables

| Variable   | Description                       | Default (sandbox)           |
|------------|-----------------------------------|-----------------------------|
| `EMAIL`    | Sandbox account email             | `candidate1@onsetto.test`   |
| `PASSWORD` | Sandbox account password          | `Password123!`              |
| `MFA_CODE` | MFA verification code             | `1234`                      |

> Note: The browser challenge accepts any MFA code.

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
8. Prints `Part 1 complete` on success, or saves `error_screenshot.png` on failure.

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
Authenticating...
✓ MFA token received
✓ Access token received

Banking updated:
Routing: •••••0021
Account: ••••••7890

Payment updated:
Brand: visa
Last4: 4242
Expiry: 12/2027

✓ Challenge completed successfully
```
---

## Testing
Unit tests are implemented using `pytest` and use mocked HTTP responses to avoid consuming API rate limits.

Run the test suite:
```bash
pytest --cov=api
```
Current Coverage:

- `api/__init__.py` → 100%
- `api/account.py`  →  100%
- `api/auth.py`  →  95%
- `api/client.py`  →  59%
- `api/exceptions.py`  →  100%


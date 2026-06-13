"""
Account service — banking + payment update calls.

Both endpoints return a masked confirmation object on success, e.g.:
  { "routing_number": "***0021", "account_number": "***6789" }
  { "card_number": "***1111", "cardholder_name": "Test User" }

Errors handled:
  400 / 422 — validation failure (bad routing, non-Luhn card, etc.)
  401       — token expired or missing
  429       — rate limit
  5xx       — server error (surfaced as-is)
"""

from __future__ import annotations

import logging
from typing import Any

from requests import HTTPError

from api.client import APIClient
from api.exceptions import AccountUpdateError, ValidationError

log = logging.getLogger(__name__)


class AccountService:
    def __init__(self, client: APIClient) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Banking
    # ------------------------------------------------------------------

    def update_banking(self, routing: str, account: str) -> dict[str, Any]:
        """PUT /account/banking — returns masked confirmation."""
        resp = self.client.request(
            "PUT",
            "/account/banking",
            json={"routing_number": routing, "account_number": account},
        )
        return self._handle_response(resp, "banking")

    # ------------------------------------------------------------------
    # Payment
    # ------------------------------------------------------------------

    def update_payment(
        self,
        name: str,
        number: str,
        expiry: str,
        cvc: str,
    ) -> dict[str, Any]:
        """PUT /account/payment — returns masked confirmation."""
        resp = self.client.request(
            "PUT",
            "/account/payment",
            json={
                "cardholder_name": name,
                "card_number": number,
                "expiry": expiry,
                "cvc": cvc,
            },
        )
        return self._handle_response(resp, "payment")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_response(resp: Any, label: str) -> dict[str, Any]:
        if resp.status_code in (400, 422):
            body = resp.json() if resp.content else {}
            detail = body.get("detail") or body.get("message") or resp.text
            raise ValidationError(f"Validation error on {label} update: {detail}")

        if resp.status_code == 401:
            raise AccountUpdateError(
                f"Unauthorized on {label} update — token may be expired."
            )

        if resp.status_code == 429:
            raise AccountUpdateError(
                f"Rate-limited on {label} update. Wait and retry."
            )

        try:
            resp.raise_for_status()
        except HTTPError as exc:
            raise AccountUpdateError(
                f"{label} update failed ({resp.status_code}): {resp.text}"
            ) from exc

        return resp.json()

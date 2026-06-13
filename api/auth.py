"""
Authentication service — login + MFA flow.

Flow:
  1. POST /auth/token  →  { mfa_token, ... }
  2. POST /auth/mfa/verify  →  { access_token, ... }

The access_token is stored on the client so subsequent requests are
automatically authorised.
"""

from __future__ import annotations

import logging
from typing import Any

from requests import HTTPError

from api.client import APIClient
from api.exceptions import AuthError, MFAError

log = logging.getLogger(__name__)


class AuthService:
    def __init__(self, client: APIClient) -> None:
        self.client = client

    def login(self, username: str, password: str) -> dict[str, Any]:
        """POST /auth/token — returns the raw response payload."""
        resp = self.client.request(
            "POST",
            "/auth/token",
            json={"username": username, "password": password},
        )

        if resp.status_code == 401:
            raise AuthError("Invalid credentials — check USERNAME / PASSWORD.")
        if resp.status_code == 429:
            raise AuthError("Rate-limited on login. Wait a moment and try again.")

        try:
            resp.raise_for_status()
        except HTTPError as exc:
            raise AuthError(f"Login failed ({resp.status_code}): {resp.text}") from exc

        payload = resp.json()
        log.debug("Login successful — mfa_token present: %s", "mfa_token" in payload)
        return payload

    def verify_mfa(self, mfa_token: str, code: str) -> str:
        """POST /auth/mfa/verify — stores and returns the bearer token."""
        resp = self.client.request(
            "POST",
            "/auth/mfa/verify",
            json={"mfa_token": mfa_token, "code": code},
        )

        if resp.status_code == 401:
            raise MFAError("MFA verification failed — wrong token or code.")
        if resp.status_code == 429:
            raise MFAError("Rate-limited on MFA. Wait a moment and try again.")

        try:
            resp.raise_for_status()
        except HTTPError as exc:
            raise MFAError(f"MFA verify failed ({resp.status_code}): {resp.text}") from exc

        access_token: str = resp.json()["access_token"]
        self.client.token = access_token
        log.debug("MFA verified — bearer token acquired")
        return access_token

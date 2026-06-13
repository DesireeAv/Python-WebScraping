from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import requests


class APIError(Exception):
    def __init__(self, status_code: int, message: str, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.details = details


@dataclass
class AuthTokens:
    mfa_token: str
    access_token: str


class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.access_token: Optional[str] = None

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _headers(self, auth: bool = False) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if auth:
            if not self.access_token:
                raise APIError(401, "Missing access token")
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        auth: bool = False,
    ) -> dict[str, Any] | list[Any]:
        try:
            response = self.session.request(
                method=method,
                url=self._url(path),
                json=json,
                headers=self._headers(auth=auth),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise APIError(0, f"Network error: {exc}") from exc

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            msg = "Rate limited (429)"
            if retry_after:
                msg += f"; retry after {retry_after} seconds"
            raise APIError(429, msg, self._safe_json(response))

        if response.status_code >= 400:
            payload = self._safe_json(response)
            message = self._extract_message(payload) or response.text.strip() or "Request failed"

            if response.status_code == 401:
                raise APIError(401, f"Unauthorized: {message}", payload)
            if response.status_code == 403:
                raise APIError(403, f"Forbidden: {message}", payload)
            if response.status_code == 400:
                raise APIError(400, f"Validation error: {message}", payload)

            raise APIError(response.status_code, message, payload)

        return self._safe_json(response)

    def _safe_json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    def _extract_message(self, payload: Any) -> str:
        if isinstance(payload, dict):
            for key in ("message", "error", "detail", "details"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return ""

    def login(self, email: str, password: str) -> str:
        payload = self._request(
            "POST",
            "/auth/token",
            json={"email": email, "password": password},
            auth=False,
        )

        if not isinstance(payload, dict) or "mfa_token" not in payload:
            raise APIError(500, "Unexpected /auth/token response", payload)

        return str(payload["mfa_token"])

    def verify_mfa(self, mfa_token: str, code: str = "1234") -> str:
        payload = self._request(
            "POST",
            "/auth/mfa/verify",
            json={"mfa_token": mfa_token, "code": code},
            auth=False,
        )

        if not isinstance(payload, dict) or "access_token" not in payload:
            raise APIError(500, "Unexpected /auth/mfa/verify response", payload)

        self.access_token = str(payload["access_token"])
        return self.access_token

    def update_banking(self, routing_number: str, account_number: str) -> dict[str, Any]:
        payload = self._request(
            "PUT",
            "/account/banking",
            json={
                "routing_number": routing_number,
                "account_number": account_number,
            },
            auth=True,
        )

        if not isinstance(payload, dict):
            raise APIError(500, "Unexpected /account/banking response", payload)

        return payload

    def update_payment(
        self,
        cardholder_name: str,
        card_number: str,
        exp_month: int,
        exp_year: int,
        cvc: str,
    ) -> dict[str, Any]:
        payload = self._request(
            "PUT",
            "/account/payment",
            json={
                "cardholder_name": cardholder_name,
                "card_number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
            auth=True,
        )

        if not isinstance(payload, dict):
            raise APIError(500, "Unexpected /account/payment response", payload)

        return payload
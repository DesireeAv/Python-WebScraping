"""
api package — Python client for the Onsetto challenge API.

Usage:
    from api import APIClient, AuthService, AccountService
"""

from api.client import APIClient
from api.auth import AuthService
from api.account import AccountService
from api.exceptions import (
    ChallengeAPIError,
    AuthError,
    MFAError,
    ValidationError,
    AccountUpdateError,
)

__all__ = [
    "APIClient",
    "AuthService",
    "AccountService",
    "ChallengeAPIError",
    "AuthError",
    "MFAError",
    "ValidationError",
    "AccountUpdateError",
]

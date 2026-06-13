"""Custom exception types for the API client."""


class ChallengeAPIError(Exception):
    """Base error for all API-layer failures."""


class AuthError(ChallengeAPIError):
    """Raised when login or token exchange fails."""


class MFAError(ChallengeAPIError):
    """Raised when MFA verification fails."""


class ValidationError(ChallengeAPIError):
    """Raised when the server rejects input (422)."""


class AccountUpdateError(ChallengeAPIError):
    """Raised when an account update call fails."""

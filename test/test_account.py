from unittest.mock import Mock

import pytest
from requests import HTTPError

from api.account import AccountService
from api.exceptions import (
    AccountUpdateError,
    ValidationError,
)


def test_update_banking_success():
    client = Mock()

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "routing_masked": "•••••0021",
        "account_masked": "••••••7890",
    }

    client.request.return_value = response

    service = AccountService(client)

    result = service.update_banking(
        "021000021",
        "1234567890",
    )

    assert result["routing_masked"].endswith("0021")
    assert result["account_masked"].endswith("7890")


def test_update_payment_success():
    client = Mock()

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "card_brand": "visa",
        "last4": "4242",
    }

    client.request.return_value = response

    service = AccountService(client)

    result = service.update_payment(
        "Test User",
        "4242424242424242",
        "12/27",
        "123",
    )

    assert result["last4"] == "4242"


def test_validation_error_400():
    client = Mock()

    response = Mock()
    response.status_code = 400
    response.content = b"content"
    response.json.return_value = {
        "message": "bad routing"
    }

    client.request.return_value = response

    service = AccountService(client)

    with pytest.raises(ValidationError):
        service.update_banking(
            "123",
            "456",
        )


def test_validation_error_422():
    client = Mock()

    response = Mock()
    response.status_code = 422
    response.content = b"content"
    response.json.return_value = {
        "detail": "invalid card"
    }

    client.request.return_value = response

    service = AccountService(client)

    with pytest.raises(ValidationError):
        service.update_payment(
            "Test User",
            "1111",
            "01/20",
            "123",
        )


def test_account_401():
    client = Mock()

    response = Mock()
    response.status_code = 401

    client.request.return_value = response

    service = AccountService(client)

    with pytest.raises(AccountUpdateError):
        service.update_banking(
            "021000021",
            "1234567890",
        )


def test_account_429():
    client = Mock()

    response = Mock()
    response.status_code = 429

    client.request.return_value = response

    service = AccountService(client)

    with pytest.raises(AccountUpdateError):
        service.update_banking(
            "021000021",
            "1234567890",
        )


def test_account_http_error():
    client = Mock()

    response = Mock()
    response.status_code = 500
    response.raise_for_status.side_effect = HTTPError()

    client.request.return_value = response

    service = AccountService(client)

    with pytest.raises(AccountUpdateError):
        service.update_banking(
            "021000021",
            "1234567890",
        )
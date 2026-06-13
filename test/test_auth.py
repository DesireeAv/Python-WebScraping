from unittest.mock import Mock

import pytest
from requests import HTTPError

from api.auth import AuthService
from api.exceptions import AuthError, MFAError


def test_login_success():
    client = Mock()

    response = Mock()
    response.status_code = 200
    response.json.return_value = {"mfa_token": "abc"}

    client.request.return_value = response

    service = AuthService(client)

    result = service.login("user", "pass")

    assert result["mfa_token"] == "abc"


def test_login_401():
    client = Mock()

    response = Mock()
    response.status_code = 401

    client.request.return_value = response

    service = AuthService(client)

    with pytest.raises(AuthError):
        service.login("user", "badpass")


def test_login_429():
    client = Mock()

    response = Mock()
    response.status_code = 429

    client.request.return_value = response

    service = AuthService(client)

    with pytest.raises(AuthError):
        service.login("user", "pass")


def test_login_http_error():
    client = Mock()

    response = Mock()
    response.status_code = 500
    response.raise_for_status.side_effect = HTTPError()

    client.request.return_value = response

    service = AuthService(client)

    with pytest.raises(AuthError):
        service.login("user", "pass")


def test_verify_mfa_success():
    client = Mock()

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "access_token": "token123"
    }

    client.request.return_value = response

    service = AuthService(client)

    token = service.verify_mfa("mfa", "1234")

    assert token == "token123"
    assert client.token == "token123"


def test_verify_mfa_401():
    client = Mock()

    response = Mock()
    response.status_code = 401

    client.request.return_value = response

    service = AuthService(client)

    with pytest.raises(MFAError):
        service.verify_mfa("mfa", "0000")


def test_verify_mfa_429():
    client = Mock()

    response = Mock()
    response.status_code = 429

    client.request.return_value = response

    service = AuthService(client)

    with pytest.raises(MFAError):
        service.verify_mfa("mfa", "1234")
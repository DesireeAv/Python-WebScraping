import pytest
from unittest.mock import Mock, patch
from api.client import APIClient, APIError

def test_bad_credentials():
    client = APIClient("https://example.com")

    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "message": "Invalid credentials"
    }

    with patch.object(
        client.session,
        "request",
        return_value=mock_response,
    ):
        with pytest.raises(APIError):
            client.login(
                "bad@example.com",
                "wrong"
            )


from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request

import auth
from auth.jwttoken.token import TokenService, TokenProvider
from auth.model.user import User
from auth.userProvider import ValidateAndReturnUser


class MockTokenService(TokenService):
    def get_token_provider(self) -> TokenProvider:
        pass

    def decode_and_check_authorization(self, expected_roles, request):
        return User(
            name="Dummy",
        )


@pytest.fixture(autouse=True)
def setup():
    auth.init()


def test_validate_and_return_user():
    expected_roles = ["admin"]
    user_provider = ValidateAndReturnUser(expected_roles)
    request = MagicMock(spec=Request)
    request.headers = {"Authorization": "Bearer some_token"}
    with patch("auth.userProvider.get_token_service") as mock_get_token_service:
        mock_get_token_service.return_value = MockTokenService()
        user = user_provider(request)
        assert user.name == "Dummy"

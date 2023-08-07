from auth.jwttoken.token_service import DefaultTokenService, DummyTokenProvider


def test_default_token_service():
    token_provider = DummyTokenProvider()
    token_service = DefaultTokenService(token_provider)
    user = token_service.decode_and_check_authorization(["admin"])
    assert user is not None
    assert user.name == "Dummy User"

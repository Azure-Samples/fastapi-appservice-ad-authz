from auth.jwttoken.token_stub import DummyTokenProvider


def test_dummy_token_provider():
    token_provider = DummyTokenProvider()
    token = token_provider.get_id_and_access_token()
    assert token is not None
    assert token.access_token is not None
    assert token.id_token is not None

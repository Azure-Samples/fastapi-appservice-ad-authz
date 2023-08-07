import datetime
import logging

from jose import jwt

from auth.jwttoken.token import IdAndAccessToken, TokenProvider
from config import get_settings

log = logging.getLogger(__name__)
settings = get_settings()


class DummyTokenProvider(TokenProvider):
    """Provides token when the application is not backed by any auth. This primarily created to that rest of
    application code is abstracted out from knowing if they are behind auth or no. It will give Admin role for
    CP_AUTH_BYPASS_ENV. This should never be initialized in production as prod is expected to always have auth
    """

    def get_id_and_access_token(self, **kwargs) -> IdAndAccessToken:
        """This method generates an ID token and an access token using the provided payload and secret key. The payload includes the user ID, expiration time, Azure tenant ID,
        Azure client ID, key ID, and user name. The access token is encoded using the JWT algorithm 'HS256' and the provided secret key. The ID token is also encoded using the
        same algorithm and secret key. The ID token payload includes the groups and email fields. The method returns an instance of the IdAndAccessToken class,
        which contains the generated access token and ID token."""
        payload_for_access_token = {
            "user_id": "Dummy",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iss": settings.AZURE_TENANT_ID,
            "audience": settings.AZURE_CLIENT_ID,
            "kid": "my_key_id",
            "name": "Dummy User",
        }
        secret_key = "my_secret_key"
        headers = {"kid": secret_key}
        access_token = jwt.encode(
            payload_for_access_token, secret_key, algorithm="HS256", headers=headers
        )
        payload_for_id_token = payload_for_access_token
        groups = [
            f"{settings.CP_APP_NAME}-{settings.CP_AUTH_BYPASS_ENV}-{settings.ADMIN_ROLE_NAME}"
        ]
        payload_for_id_token["groups"] = groups
        payload_for_id_token["email"] = "no-mail-id@invaliddomain.com"
        id_token = jwt.encode(
            payload_for_access_token, secret_key, algorithm="HS256", headers=headers
        )
        return IdAndAccessToken(access_token=access_token, id_token=id_token)

    def renew_token(self, **kwargs) -> IdAndAccessToken:
        """This method is supposed to renew the token, but in case of dummy token provider, it does nothing"""
        pass

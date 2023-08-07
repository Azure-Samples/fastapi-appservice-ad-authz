import logging
import re
from typing import Optional

from jose import ExpiredSignatureError, jwt
from jose.exceptions import JWSSignatureError

from auth import retryable_requester, add_additional_permissions_based_on_hierarchy
from auth.exception import UnAuthorizedException
from auth.http.appservice import AppServiceBasedTokenProvider
from auth.jwttoken.token import TokenService, TokenProvider, IdAndAccessToken
from auth.jwttoken.token_stub import DummyTokenProvider
from auth.model.roles import RoleCollection, Role, is_valid_role
from auth.model.user import User
from config import get_settings

settings = get_settings()
signing_keys = {}
tenant_id = settings.AZURE_TENANT_ID
client_id = settings.AZURE_CLIENT_ID
log = logging.getLogger(__name__)


def populate_signing_keys():
    """The `populate_signing_keys` function is used to retrieve and populate signing keys for authentication in a service. It requires the `tenant_id` and `client_id` parameters to be provided. If either of these parameters is `None`, an exception is raised with the message "Authentication enabled service needs tenant_id and client_id".

    The function then constructs the JSON Web Key Set (JWKS) URI using the `tenant_id` and sends a GET request to retrieve the JWKS response. The response is converted to JSON format.

    The function returns a dictionary of signing keys, where the key is the 'kid' (key ID) and the value is the key itself. The keys are filtered based on the 'kty' (key type) being 'RSA' and the 'alg' (algorithm) being 'RS256' or the default value 'RS256' if 'alg' is not present.

    """
    if tenant_id is None or client_id is None:
        raise Exception("Authentication enabled service needs tenant_id and client_id")
    jwks_uri = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
    jwks_response = retryable_requester().get(jwks_uri).json()
    return {
        key["kid"]: key
        for key in jwks_response["keys"]
        if key["kty"] == "RSA" and key.get("alg", "RS256") == "RS256"
    }


if settings.WEBSITE_AUTH_ENABLED:
    signing_keys = populate_signing_keys()


class DefaultTokenService(TokenService):
    """The `DefaultTokenService` class is an implementation of the `TokenService` interface. It provides methods for decoding tokens and checking authorization."""
    def __init__(self, token_provider: TokenProvider):
        """

        Parameters:
        - `self`: The instance of the class itself.
        - `token_provider`: An instance of the `TokenProvider` class that provides tokens.

        Returns:
        - None

        Example usage:
        ```
        token_provider = TokenProvider()
        obj = ClassName(token_provider)
        ```

        Note: The `token_provider` parameter is required and must be an instance of the `TokenProvider` class.
        """
        self.token_provider = token_provider

    def get_token_provider(self) -> TokenProvider:
        '''This method returns the token provider associated with the current object.

        Returns:
            TokenProvider: The token provider associated with the current object.
        """'''
        return self.token_provider

    def __decode(self, **kwargs) -> Optional[User]:
        """The `__decode` method is a private method that decodes a token and returns a `User` object. It takes in keyword arguments (`**kwargs`) which are passed to the `get_id_and_access_token` and `renew_token` methods of the `TokenProvider` class.

        Parameters:
        - `self`: The instance of the class that the method belongs to.

        Returns:
        - An optional `User` object if the token is successfully decoded, or `None` if the token is invalid or expired.

        Raises:
        - `ExpiredSignatureError`: If the access token has expired.

        Note:
        - This method internally calls the `__decode_token` method to decode the token obtained from the `TokenProvider`.
        - If the access token has expired, the method will log a warning message and attempt to renew the token using the `renew_token` method of the `TokenProvider` before decoding it again.
        """
        token_provider: TokenProvider = self.get_token_provider()
        try:
            return self.__decode_token(token_provider.get_id_and_access_token(**kwargs))
        except ExpiredSignatureError:
            log.warning(
                "Access token expired, trying to get a new one using the refresh token"
            )
            return self.__decode_token(token_provider.renew_token(**kwargs))

    def __decode_token(self, tokens: IdAndAccessToken) -> Optional[User]:
        """This method decodes a token using the provided `tokens` which contain an ID token and an access token. It returns an optional `User` object.

        ### Parameters:
        - `tokens` (IdAndAccessToken): An object containing an ID token and an access token.

        ### Returns:
        - `Optional[User]`: An optional `User` object representing the decoded token.

        ### Steps:
        1. Get the unverified header from the ID token using `jwt.get_unverified_header()`.
        2. Get the unverified claims from the ID token using `jwt.get_unverified_claims()`.
        3. If the app is running on an app service and website authentication is enabled, try to validate and decode the token.
        4. If the signature verification fails, refresh the signing keys and try to validate and decode the token again.
        5. Get the groups from the decoded token.
        6. Create an empty `RoleCollection` object.
        7. Iterate over each group and extract the role using a regular expression pattern.
        8. If the role is valid, create a `Role` object and add it to the `RoleCollection`.
        9. If the role is invalid, log a warning message.
        10. If the RBAC feature is not enabled, add a stub admin role to the `RoleCollection`.
        11. Create a `User` object with the decoded token, ID token, access token, role collection, and name.
        12. Return the `User` object."""
        header: dict[str, str] = jwt.get_unverified_header(token=tokens.id_token) or {}
        token = jwt.get_unverified_claims(token=tokens.id_token)
        if settings.IS_ON_APP_SERVICE and settings.WEBSITE_AUTH_ENABLED:
            try:
                token = self.__validate_and_decode(header, tokens.id_token)
            except JWSSignatureError as e:
                global signing_keys
                signing_keys = populate_signing_keys()
                token = self.__validate_and_decode(header, tokens.id_token)
        groups = token.get(settings.GROUP_NODE_IN_DECODED_TOKEN, [])
        role_collection = RoleCollection()
        for group in groups:
            match = re.match(settings.GROUP_PATTERN, group)
            if match:
                role = match.group(3)
                if is_valid_role(role):
                    role_obj = Role(match.group(1), match.group(2), role)
                    role_collection.add_roles(
                        add_additional_permissions_based_on_hierarchy(role_obj)
                    )
                else:
                    log.warning(
                        "Invalid group %s found for user that will be ignored", group
                    )
        if not settings.FEATURE_RBAC_ENABLED:
            admin_role = Role(
                app_name=settings.CP_APP_NAME,
                env=settings.CP_AUTH_BYPASS_ENV,
                role=settings.ADMIN_ROLE_NAME,
            )
            role_collection.add_role(admin_role)
        user = User(
            claims=token,
            id_token=tokens.id_token,
            access_token=tokens.access_token,
            role_collection=role_collection,
            name=token.get("name", "unknown"),
        )
        return user

    def __validate_and_decode(self, header, token):
        """This method is used to validate and decode a JWT token. It takes two parameters: `header` and `token`.

        The `header` parameter is a dictionary containing the header information of the JWT token.

        The `token` parameter is the JWT token that needs to be validated and decoded.

        The method first retrieves the signing key from a dictionary called `signing_keys` using the value of the `kid` key from the `header` dictionary.

        Then, it uses the `jwt.decode()` function to decode the `token` using the retrieved signing key. The decoding is done using the RS256 algorithm and the `client_id` is specified as the audience.

        Finally, the decoded token is returned."""
        signing_key = signing_keys.get(header["kid"])
        token = jwt.decode(
            token=token, key=signing_key, algorithms=["RS256"], audience=client_id
        )
        return token

    def decode_and_check_authorization(self, expected_roles, **kwargs) -> User:
        """This method decodes the authorization token and checks if the user is authorized based on the expected roles.

        Parameters:
        - expected_roles (list): A list of roles that the user is expected to have.

        Returns:
        - User: The user object if the user is authorized.

        Raises:
        - UnAuthorizedException: If the user is not authorized. The exception message will indicate the expected roles and the user's current roles.
        """
        user = self.__decode(**kwargs)
        if user.is_authorized(expected_roles):
            return user
        raise UnAuthorizedException(
            message=f"Not authorized. You need to be a member of the {expected_roles} roles. Your current roles are {user.role_collection}.",
            expected_roles=expected_roles,
            user_roles=user.role_collection.roles,
        )


def get_token_service() -> TokenService:
    """
        This function returns an instance of the TokenService class.
        This function checks if the WEBSITE_AUTH_ENABLED setting is True. If it is True, it creates an instance of the
        AppServiceBasedTokenProvider class and assigns it to the token_provider variable. If WEBSITE_AUTH_ENABLED is False,
        it creates an instance of the DummyTokenProvider class and assigns it to the token_provider variable.

        It then creates an instance of the DefaultTokenService class, passing the token_provider as an argument, and assigns
        it to the token_service variable.

        Finally, it returns the token_service instance.
    """
    token_provider = (
        AppServiceBasedTokenProvider()
        if settings.WEBSITE_AUTH_ENABLED
        else DummyTokenProvider()
    )
    token_service = DefaultTokenService(token_provider)
    return token_service

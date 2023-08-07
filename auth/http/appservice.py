from typing import List

from fastapi import HTTPException
from starlette.requests import Request

from auth import retryable_requester
from auth.exception import AccessTokenMissingException, IdTokenMissingException
from auth.jwttoken.token import TokenProvider, IdAndAccessToken
from config import get_settings

settings = get_settings()


class AppServiceBasedTokenProvider(TokenProvider):
    """
    A token provider that retrieves access and ID tokens from Azure App Service headers.

    This token provider is designed to work with Azure App Service authentication and authorization.
    It retrieves the access and ID tokens from the headers of the incoming request, and uses them to
    authenticate and authorize the user.

    This token provider is used by the `AuthMiddleware` to authenticate and authorize incoming requests.
    """

    def get_id_and_access_token(self, **kwargs) -> IdAndAccessToken:
        """
        Retrieves the access and ID tokens from the headers of the incoming request.

        This method is used to retrieve the access and ID tokens from the headers of the incoming request,
        and returns them as an instance of the `IdAndAccessToken` class.

        :param request: The incoming request.
        :type request: Request
        :raises AccessTokenMissingException: If the access token is missing from the request headers.
        :raises IdTokenMissingException: If the ID token is missing from the request headers.
        :return: An instance of the `IdAndAccessToken` class containing the access and ID tokens.
        :rtype: IdAndAccessToken
        """
        if kwargs["request"] is None:
            raise ValueError("Request is required argument")
        access_token = kwargs["request"].headers.get(
            settings.APP_SERVICE_ACCESS_TOKEN_HEADER
        )
        if access_token is None:
            raise AccessTokenMissingException("Access Token is missing")
        id_token = kwargs["request"].headers.get(settings.APP_SERVICE_ID_TOKEN_HEADER)
        if id_token is None:
            raise IdTokenMissingException("Id token is not found")
        return IdAndAccessToken(access_token=access_token, id_token=id_token)

    def renew_token(self, **kwargs) -> List[dict]:
        """
        Renews the access token by refreshing it with the Azure App Service authentication endpoint.

        This method is used to renew the access token by refreshing it with the Azure App Service authentication endpoint.
        It retrieves the request object from the keyword arguments, and uses it to refresh the access token.

        :param request: The incoming request.
        :type request: Request
        :raises HTTPException: If the request is not authorized.
        :return: A list of dictionaries containing the renewed access token.
        :rtype: List[dict]
        """
        if kwargs["request"] is None:
            raise ValueError("Request is required argument")
        return self.__get_new_token(kwargs["request"])

    def __get_new_token(self, request: Request) -> List[dict]:
        """
        Retrieves a new access token by refreshing the current access token.

        This method is used to retrieve a new access token by refreshing the current access token.
        It first refreshes the current access token by calling the `__refresh_token` method, and then
        retrieves the new access token from the Azure App Service authentication endpoint.

        :param request: The incoming request.
        :type request: Request
        :raises HTTPException: If the request is not authorized.
        :return: A list of dictionaries containing the new access token.
        :rtype: List[dict]
        """
        self.__refresh_token(request)
        s = retryable_requester()
        new_token = s.get(
            f"{request.base_url}.auth/me", timeout=5, cookies=request.cookies
        )
        if new_token.status_code == 200:
            return new_token.json()
        raise HTTPException(status_code=403, detail="Not authorized.")

    @staticmethod
    def __refresh_token(request: Request) -> None:
        """
        Refreshes the current access token.

        This method is used to refresh the current access token by calling the Azure App Service authentication endpoint.
        It retrieves the request object from the keyword arguments, and uses it to refresh the access token.

        :param request: The incoming request.
        :type request: Request
        :raises HTTPException: If the request is not authorized.
        :return: None
        """
        s = retryable_requester()
        esp = s.get(
            f"{request.base_url}.auth/refresh",
            timeout=5,
            cookies=request.cookies,
            headers=request.headers,
        )
        if esp.status_code == 200:
            return
        raise HTTPException(
            status_code=403,
            detail="Not authorized. Please refresh the page to re-initiate login.",
        )

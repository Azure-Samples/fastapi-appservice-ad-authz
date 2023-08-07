import logging
from typing import Optional

from fastapi import HTTPException, Request
from starlette import status

from auth import is_initialized
from auth.exception import (
    IdTokenMissingException,
    AccessTokenMissingException,
    UnAuthorizedException,
    AuthInitializationException,
)
from auth.jwttoken.token_service import get_token_service
from auth.model.user import User
from config import get_settings

log = logging.getLogger(__name__)
settings = get_settings()


class ValidateAndReturnUser:
    """The `ValidateAndReturnUser` class is responsible for validating user authentication and authorization based on the expected roles provided during initialization. It is designed to be used as a callable object."""

    def __init__(self, expected_roles: list[str]) -> None:
        """The `__init__` method is the constructor for the class. It initializes an instance of the class and sets the `expected_roles` attribute.

        Parameters:
        - `expected_roles` (list[str]): A list of expected roles for the user. Defaults to an empty list if not provided.

        Raises:
        - `AuthInitializationException`: If the framework is not initialized before using this class.

        Returns:
        - None"""
        if not is_initialized():
            raise AuthInitializationException(
                "Framework is not initialized. Please call init() before using this class"
            )
        self.expected_roles = expected_roles or []

    def __call__(self, request: Request) -> Optional[User]:
        """The `__call__` method is a special method in Python classes that allows an instance of the class to be called as a function. In this case, the `__call__` method takes a `request` parameter of type `Request` and returns an optional `User` object.

        The method first creates a dummy `User` object with some default values. Then, it tries to decode and check the authorization of the user's token using the `get_token_service().decode_and_check_authorization` method. If the token is missing or invalid, it logs an error and raises an `HTTPException` with a status code of 401 (Unauthorized) and a detail message of "Not authenticated".

        If the user is authenticated but not authorized, it logs an error and raises an `HTTPException` with a status code of 403 (Forbidden) and a detail message indicating the expected roles and the user's current roles.

        Finally, the method returns the `User` object.

        Note: The method assumes the existence of certain exception classes (`IdTokenMissingException`, `AccessTokenMissingException`, `UnAuthorizedException`) and a logger (`log`). It also references a `get_token_service()` function. These details are not provided in the code snippet and should be defined elsewhere.
        """
        user = User(
            id_token="Some dummy id token that won't be used",
            name="Dummy",
            access_token="some dummy access token",
            role_collection=None,
            claims={"email": "no-mail-id@invaliddomain.com"},
        )
        try:
            user = get_token_service().decode_and_check_authorization(
                self.expected_roles, request=request
            )
        except (IdTokenMissingException, AccessTokenMissingException) as exp:
            log.error(exp)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except UnAuthorizedException as exp:
            log.error(exp)
            raise HTTPException(
                status_code=403,
                detail=f"Not authorized. You need to be a member of the {self.expected_roles} roles. Your current roles are {user.role_collection}",
            )
        return user

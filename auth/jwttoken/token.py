import logging
from abc import ABC, abstractmethod

from auth.model.user import User
from config import get_settings

settings = get_settings()
log = logging.getLogger(__name__)


class IdAndAccessToken:
    """The `IdAndAccessToken` class represents an object that holds an access token and an ID token. It has a constructor method `__init__` that takes in two parameters: `access_token` and `id_token`. These parameters are used to initialize the `access_token` and `id_token` attributes of the object.

    Example usage:

    ```python
    # Create an instance of IdAndAccessToken
    token = IdAndAccessToken("access_token_value", "id_token_value")

    # Access the access_token and id_token attributes
    print(token.access_token)  # Output: "access_token_value"
    print(token.id_token)  # Output: "id_token_value"
    ```

    Note: This class does not have any additional methods or functionality."""

    def __init__(self, access_token, id_token):
        self.access_token = access_token
        self.id_token = id_token


class TokenProvider(ABC):
    """Class: TokenProvider

    This class is an abstract base class (ABC) that provides a blueprint for token providers. It defines two abstract methods that need to be implemented by subclasses.

    Methods:
    1. get_id_and_access_token(self, **kwargs) -> IdAndAccessToken:
       - This abstract method is responsible for retrieving the raw access token.
       - Parameters: **kwargs (keyword arguments) - additional arguments that can be passed to the method.
       - Returns: An instance of the IdAndAccessToken class, which represents the ID and access token.

    2. renew_token(self, **kwargs) -> IdAndAccessToken:
       - This abstract method is responsible for renewing the token.
       - Parameters: **kwargs (keyword arguments) - additional arguments that can be passed to the method.
       - Returns: An instance of the IdAndAccessToken class, which represents the renewed ID and access token.
    """

    @abstractmethod
    def get_id_and_access_token(self, **kwargs) -> IdAndAccessToken:
        """Return raw access token"""

    @abstractmethod
    def renew_token(self, **kwargs) -> IdAndAccessToken:
        """This method is supposed to renew the token"""


class TokenService(ABC):
    """The `TokenService` class is an abstract base class (ABC) that provides methods for working with tokens and authorization.

    Methods:
    - `get_token_provider(self) -> TokenProvider`: This method is abstract and must be implemented by subclasses. It returns an instance of the `TokenProvider` class, which is responsible for generating and managing tokens.

    - `decode_and_check_authorization(self, expected_roles, **kwargs) -> User`: This method is abstract and must be implemented by subclasses. It takes in a list of expected roles and additional keyword arguments, and returns a `User` object if the token is valid and the user has the required roles. It decodes the token and checks the authorization based on the expected roles.

    Note: Subclasses of `TokenService` should implement these abstract methods to provide the necessary functionality for working with tokens and authorization.
    """

    @abstractmethod
    def get_token_provider(self) -> TokenProvider:
        """implement get token Provider"""

    @abstractmethod
    def decode_and_check_authorization(self, expected_roles, **kwargs) -> User:
        """implement decode token and check auth"""

class AccessTokenMissingException(Exception):
    """This class represents an exception that is raised when an access token is missing. It is a subclass of the built-in `Exception` class.
    #### Attributes:
    - `message`: A string representing the error message.

    #### Methods:
    - `__init__(self, message, **kwargs)`: Initializes the exception with the given error message. The `message` parameter is required, and any additional keyword arguments can be passed as `**kwargs`.
    """

    def __init__(self, message, **kwargs):
        super().__init__(message)


class IdTokenMissingException(Exception):
    """This class represents an exception that is raised when an ID token is missing. It is a subclass of the built-in `Exception` class.

    The `IdTokenMissingException` class has a constructor that takes a `message` parameter, which is the error message associated with the exception. The constructor calls the constructor of the parent `Exception` class with the `message` parameter.

    No additional methods or attributes are defined in this class."""

    def __init__(self, message, **kwargs):
        super().__init__(message)


class UnAuthorizedException(Exception):
    """The `UnAuthorizedException` class is a custom exception class that is raised when a user is not authorized to perform a certain action. It inherits from the built-in `Exception` class.

    Attributes:
    - `message` (str): The error message associated with the exception.
    - `user_roles` (list or None): The roles of the user who triggered the exception.
    - `expected_roles` (list or None): The roles that were expected for the user to perform the action.

    Methods:
    - `__init__(self, message, **kwargs)`: Initializes the exception with the given error message and optional keyword arguments. The `user_roles` and `expected_roles` are extracted from the keyword arguments and assigned to their respective attributes.
    """

    def __init__(self, message, **kwargs):
        """The `__init__` method is a special method in Python classes that is automatically called when an object is created from the class. It initializes the object's attributes and performs any necessary setup."""
        super().__init__(message)
        self.user_roles = kwargs.pop("user_roles", None)
        self.message = message
        self.expected_roles = kwargs.pop("expected_roles", None)


class AuthInitializationException(Exception):
    """This class represents an exception that is raised when there is an error during the initialization of authentication. It is a subclass of the built-in `Exception` class.

    #### Methods:

    - `__init__(*args: object) -> None`: Initializes the exception with the given arguments. Calls the `__init__` method of the parent `Exception` class.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidRoleException(Exception):
    """The `InvalidRoleException` class is a custom exception class that is raised when an invalid role is encountered. It inherits from the base `Exception` class.

    #### Methods:

    - `__init__(self, message)`: Initializes the exception with the given error message. The `message` parameter is a string that describes the reason for the exception.

    #### Example usage:

    ```python
    try:
        # Some code that may raise InvalidRoleException
        raise InvalidRoleException("Invalid role encountered")
    except InvalidRoleException as e:
        print(e)
    ```

    In the example above, the `InvalidRoleException` is raised with the error message "Invalid role encountered" and then caught in the `except` block. The error message can be accessed using the `e` variable.
    """

    def __init__(self, message) -> None:
        super().__init__(message)

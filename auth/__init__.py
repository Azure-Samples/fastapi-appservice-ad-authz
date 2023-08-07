import requests
from requests.adapters import HTTPAdapter, Retry

from auth.exception import AuthInitializationException
from auth.model.roles import Role


class Singleton(type):
    """This class is a metaclass that allows the creation of singleton classes. A singleton class is a class that can only have one instance, ensuring that all instances of the class share the same state.

    The Singleton class is implemented as a metaclass, which means it is used to create other classes. When a class is created using this metaclass, the __call__ method is called whenever an instance of the class is created.

    The __call__ method checks if the class already has an instance in the _instances dictionary. If it does, it returns that instance. If not, it creates a new instance using the super().__call__(*args, **kwargs) method and stores it in the _instances dictionary before returning it.

    By using this metaclass, any class that is created with it will automatically become a singleton class. This means that only one instance of the class can exist at a time, and all instances will share the same state.

    Example usage:

    class MyClass(metaclass=Singleton):
        pass

    my_instance1 = MyClass()
    my_instance2 = MyClass()

    print(my_instance1 is my_instance2)  # Output: True"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        The purpose of this method is to implement a singleton pattern, which ensures that only one instance of the class exists. It does this by checking if the class is already present in the `_instances` dictionary attribute of the class. If it is not present, it creates a new instance of the class using the `super().__call__` method and adds it to the `_instances` dictionary. Finally, it returns the instance from the `_instances` dictionary.

        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RoleHierarchyRepository(metaclass=Singleton):
    def __init__(self):
        """sets up the initial state of the object by initializing roles as an empty dictionary."""
        self.roles: dict[str, RoleHierarchy] = {}

    def get_role_hierarchy(self, role_name: str):
        """The `get_role_hierarchy` method is used to retrieve the role hierarchy for a given role name.

        Parameters:
        - `role_name` (str): The name of the role for which the hierarchy needs to be retrieved.

        Returns:
        - The role hierarchy for the given role name, or `None` if the role name is not found in the roles dictionary.
        """
        return self.roles.get(role_name, None)

    def get_all_roles(self):
        """This method returns all the roles associated with the current object.

        @return: A list of roles
        @rtype: list"""
        return self.roles


class RoleHierarchy:
    def __init__(self, name):
        """Initialize the attributes of the object.

        Parameters:
        - `self`: The instance of the class that the method is called on.
        - `name`: A string representing the name of the object.

        Attributes:
        - `name`: A string representing the name of the object.
        - `implicit_permissions`: A list to store implicit permissions.

        Example usage:
        ```
        obj = ClassName("John")
        ```

        In the above example, the `__init__` method is called with the argument "John" to create an object of the class `ClassName` with the name attribute set to "John". The `implicit_permissions` attribute is initialized as an empty list.
        """
        self.name = name
        self.implicit_permissions = []

    def provide_implicit_permissions(self, *roleheirarchies):
        """This method, `provide_implicit_permissions`, takes in one or more `roleheirarchies` as arguments and adds them to the `implicit_permissions` list. The `roleheirarchies` are expected to be in the form of a hierarchy, where each element represents a role and its position in the hierarchy.

        Example usage:
        ```
        obj = MyClass()
        obj.provide_implicit_permissions('admin > manager > employee', 'superadmin > admin')
        ```

        In the above example, two role hierarchies are provided as arguments and added to the `implicit_permissions` list.
        """
        for hierarchy in roleheirarchies:
            self.implicit_permissions.append(hierarchy)

    def __repr__(self):
        return f"{self.name}"

    def get_all_implicit_permissions(self):
        '''"""
        This method returns a list of all implicit permissions.

        Returns:
            list: A list of all implicit permissions.
        """'''
        permissions = []
        permissions.extend(self.implicit_permissions)
        return permissions


role_hierarhcy_repo = RoleHierarchyRepository()


def add_additional_permissions_based_on_hierarchy(role: Role):
    '''"""
    This function takes a role object as input and adds additional permissions based on the role's hierarchy.

    Parameters:
    - role: A Role object representing the role for which additional permissions need to be added.

    Returns:
    - A list of Role objects representing all the roles, including the original role and any additional roles with implicit permissions based on the role's hierarchy.

    """'''
    all_roles = [Role(role.app_name, role.env, role.role_type)]
    role_type_map = role_hierarhcy_repo.get_all_roles()
    if role.role_type in role_type_map:
        for permission in role_type_map[role.role_type].get_all_implicit_permissions():
            all_roles.append(Role(role.app_name, role.env, permission.name))
    return all_roles


initialized = False


class RoleHierarchySpec:
    """The `RoleHierarchySpec` class is responsible for managing the role hierarchy in an authentication system. It provides methods for creating roles and retrieving the role hierarchy.

    Attributes:
    - `role_hierarchy_repo`: An instance of `RoleHierarchyRepository` that is used to store and retrieve role hierarchy information.

    Methods:
    - `create_role(role_name: str) -> RoleHierarchy`: Creates a new role with the given name. If the `role_hierarchy_repo` is not initialized, an `AuthInitializationException` is raised. If the role already exists, it is retrieved from the repository. If the role does not exist, a new `RoleHierarchy` object is created and added to the repository.

    Exceptions:
    - `AuthInitializationException`: Raised when the `role_hierarchy_repo` is not initialized before calling the `create_role` method.

    Example usage:
    ```python
    auth = RoleHierarchySpec()
    auth.role_hierarchy_repo = RoleHierarchyRepository()

    role = auth.create_role("admin")
    ```

    In the above example, a new `RoleHierarchy` object with the name "admin" is created and added to the `role_hierarchy_repo`.
    """

    def __init__(self):
        self.role_hierarchy_repo: RoleHierarchyRepository = None

    def create_role(self, role_name: str) -> RoleHierarchy:
        """This method creates a new role in the authentication module. It takes a role name as input and returns a RoleHierarchy object.

        Parameters:
        - role_name (str): The name of the role to be created.

        Returns:
        - RoleHierarchy: The newly created role.

        Raises:
        - AuthInitializationException: If the authentication module has not been initialized.
        """
        if self.role_hierarchy_repo is None:
            raise AuthInitializationException(
                "Please call auth.init() to initialize the auth module"
            )
        role = self.role_hierarchy_repo.get_role_hierarchy(role_name)
        if not role:
            role = RoleHierarchy(role_name)
            self.role_hierarchy_repo.roles[role_name] = role
        return role


def init() -> RoleHierarchySpec:
    """The `init` function initializes the role hierarchy specification by creating an instance of the `RoleHierarchySpec` class and setting its `role_hierarchy_repo` attribute to an instance of the `RoleHierarchyRepository` class. It also sets a global variable `initialized` to `True`. The function returns the initialized `RoleHierarchySpec` object.

    Parameters: None

    Returns:
    - `role_hierarchy_spec` (RoleHierarchySpec): The initialized role hierarchy specification object.
    """
    global initialized
    initialized = True
    role_hierarhcy_spec = RoleHierarchySpec()
    role_hierarhcy_spec.role_hierarchy_repo = RoleHierarchyRepository()
    return role_hierarhcy_spec


def retryable_requester():
    '''"""
    This function creates a retryable requester object using the requests library. It sets up a session and configures the session to automatically retry requests in case of certain HTTP status codes (500, 502, 503, 504). The maximum number of retries is set to 3, and a backoff factor of 0.5 is used to increase the delay between retries. The function returns the retryable requester object.

    Parameters:
        None

    Returns:
        A retryable requester object that can be used to make HTTP requests with automatic retries.

    Example usage:
        requester = retryable_requester()
        response = requester.get('https://example.com')
    """'''
    s = requests.session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def is_initialized():
    '''"""
    This function checks if a variable named 'initialized' has been initialized or not.

    Returns:
        bool: True if the variable 'initialized' has been initialized, False otherwise.
    """'''
    return initialized

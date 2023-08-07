from config import get_settings

settings = get_settings()


class Role:
    """The `Role` class represents a role in a system. It has three attributes: `app_name`, `env`, and `role_type`. The `__init__` method is the constructor that initializes these attributes. The `__repr__` method returns a string representation of the `Role` object. The `get_role_in_group_format` method returns a formatted string representing the role in a specific format.

    Example usage:

    ```python
    role = Role("my_app", "dev", "admin")
    print(role)  # Output: Role(app_name='my_app', env='dev', role='admin')

    group_format = role.get_role_in_group_format()
    print(group_format)  # Output: my_app-dev-admin
    ```
    """

    def __init__(self, app_name, env, role):
        """The `__init__` method is a special method in Python classes that is automatically called when an object is created from the class. It initializes the object's attributes with the provided values.

        Parameters:
        - `app_name` (str): The name of the application.
        - `env` (str): The environment in which the application is running.
        - `role` (str): The role type of the application.

        Attributes:
        - `app_name` (str): The name of the application.
        - `env` (str): The environment in which the application is running.
        - `role_type` (str): The role type of the application.

        Example usage:
        ```
        my_app = MyApp("My Application", "Production", "Admin")
        ```

        In the above example, an object `my_app` is created from the `MyApp` class with the provided values for `app_name`, `env`, and `role`. The `__init__` method initializes the `app_name`, `env`, and `role_type` attributes of the `my_app` object with the provided values.
        """
        self.app_name = app_name
        self.env = env
        self.role_type = role

    def __repr__(self):
        """The `__repr__` method is used to provide a string representation of an object. In this case, it returns a formatted string that includes the values of the `app_name`, `env`, and `role_type` attributes of the object.

        The returned string has the following format: `Role(app_name='{self.app_name}', env='{self.env}', role='{self.role_type}')`.

        This method is typically used for debugging and logging purposes, as it provides a concise and informative representation of the object.
        """
        return f"Role(app_name='{self.app_name}', env='{self.env}', role='{self.role_type}')"

    def get_role_in_group_format(self):
        """This method returns a formatted string representing the role in a group. The format of the string is "{app_name}-{env}-{role_type}"."""
        return f"{self.app_name}-{self.env}-{self.role_type}"


class RoleCollection:
    """The `RoleCollection` class represents a collection of roles. It provides methods to add roles, retrieve roles based on type, retrieve roles in a specific format, retrieve roles based on environment and type, and retrieve the unique environments in which roles exist.

    Methods:
    - `add_role(role)`: Adds a single role to the collection.
    - `add_roles(roles)`: Adds multiple roles to the collection.
    - `get_rbac_by_type(role_type)`: Retrieves roles of a specific type. Returns a dictionary where the keys are the role types and the values are lists of roles.
    - `get_in_group_format(role_type=None)`: Retrieves roles in a specific format. If `role_type` is provided, only roles of that type are returned. Otherwise, all roles are returned. Returns a list of roles in the specified format.
    - `get_rbac_by_env_and_type(env, role_type)`: Retrieves roles based on environment and type. Returns a list of roles that match the specified environment and type.
    - `get_environments()`: Retrieves the unique environments in which roles exist. Returns a set of environments.
    - `__repr__()`: Returns a string representation of the `RoleCollection` object.

    Example usage:
    ```
    rc = RoleCollection()
    rc.add_role(role1)
    rc.add_roles([role2, role3])
    rbac = rc.get_rbac_by_type('admin')
    group_format = rc.get_in_group_format()
    env_roles = rc.get_rbac_by_env_and_type('dev', 'user')
    environments = rc.get_environments()
    print(rc)
    ```

    Note: This code assumes the existence of a `Role` class with attributes `role_type` and `env`.
    """

    def __init__(self):
        """The `__init__` method is a special method in Python that is automatically called when an object is created from a class. It is used to initialize the attributes of the object.

        In this case, the `__init__` method takes in one parameter, `self`, which refers to the instance of the object being created. Inside the method, it initializes the `roles` attribute as an empty list.

        This method does not return anything."""
        self.roles = []

    def add_role(self, role):
        """This method adds a role to the list of roles for the object.

        Parameters:
        - role: The role to be added to the list of roles.

        Returns:
        None"""
        self.roles.append(role)

    def add_roles(self, roles):
        """The `add_roles` method is used to add new roles to an existing list of roles for an object. It takes in a parameter `roles`, which is a list of roles to be added. The method extends the existing list of roles with the new roles provided.

        Parameters:
        - `roles` (list): A list of roles to be added to the existing list of roles.

        Returns:
        - None

        Example usage:
        ```
        obj = MyClass()
        obj.roles = ['admin', 'user']
        new_roles = ['manager', 'guest']
        obj.add_roles(new_roles)
        print(obj.roles)  # Output: ['admin', 'user', 'manager', 'guest']
        ```"""
        self.roles.extend(roles)

    def get_rbac_by_type(self, role_type):
        """This method takes in a role_type as a parameter and returns a dictionary containing all the roles of that type. The dictionary is structured such that the role_type is the key and the value is a list of roles that match the given role_type. The method iterates over the list of roles and filters out the roles that do not match the given role_type. The resulting dictionary is then returned."""
        return {
            role.role_type: [role for role in self.roles if role.role_type == role_type]
            for role in self.roles
            if role.role_type == role_type
        }

    def get_in_group_format(self, role_type=None):
        """The `get_in_group_format` method is used to retrieve the role information in a specific format for a given group.

        Parameters:
        - `role_type` (optional): Specifies the type of role to filter the results. If not provided, all roles will be included.

        Returns:
        - A list of role information in the specified format for the group.

        Example usage:
        ```
        group = Group()
        group.get_in_group_format(role_type='admin')
        ```

        """
        return [
            role.get_role_in_group_format()
            for role in self.roles
            if role_type is None or role.role_type == role_type
        ]

    def get_rbac_by_env_and_type(self, env, role_type):
        """This method takes in two parameters: `env` and `role_type`. It returns a list of roles that match the given environment and role type.

        Parameters:
        - `env` (str): The environment to filter the roles by.
        - `role_type` (str): The role type to filter the roles by.

        Returns:
        - `roles` (list): A list of roles that match the given environment and role type.
        """
        roles = []
        for role in self.roles:
            if role.env == env and role.role_type == role_type:
                roles.append(role)
        return roles

    def get_environments(self):
        '''This method returns a set of environments associated with the roles in the current object.

        ###Detailed python docstring:

        """
        This method retrieves the environments associated with the roles in the current object.

        Returns:
            set: A set of environments.

        Example:
            >>> obj = MyClass()
            >>> obj.get_environments()
            {'dev', 'test', 'prod'}
        """'''
        return {role.env for role in self.roles}

    def __repr__(self):
        """The `__repr__` method is a special method in Python that returns a string representation of an object. In this case, the `__repr__` method is defined for a class called `RoleCollection`.

        The `__repr__` method returns a string that represents the object. It uses an f-string to format the string, including the value of the `roles` attribute of the object. The returned string has the format "RoleCollection(roles=<value of self.roles>)".

        This method is typically used for debugging and logging purposes, as it provides a concise and informative representation of the object.
        """
        return f"RoleCollection(roles={self.roles})"


def is_valid_role(role: str) -> bool:
    """The `is_valid_role` function takes a role as input and checks if it is a valid role. It returns a boolean value indicating whether the role is valid or not.

    Parameters:
    - `role` (str): The role to be checked for validity.

    Returns:
    - `bool`: True if the role is valid, False otherwise.

    Example usage:
    ```python
    is_valid_role("admin")  # True
    is_valid_role("user")  # True
    is_valid_role("guest")  # False
    ```"""
    acceptable_roles = settings.VALID_ROLES.split(",")
    return role.lower() in acceptable_roles

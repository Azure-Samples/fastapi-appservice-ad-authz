from auth.model.roles import RoleCollection
from config import get_settings

settings = get_settings()


class User:
    def __init__(
        self,
        id_token: str = None,
        name: str = None,
        access_token: str = None,
        role_collection=None,
        claims=None,
    ) -> None:
        """The `__init__` method is the constructor for a class. It initializes the object with the provided parameters.

        Parameters:
        - `id_token` (str): The ID token for the user. Default is `None`.
        - `name` (str): The name of the user. Default is `None`.
        - `access_token` (str): The access token for the user. Default is `None`.
        - `role_collection` (RoleCollection): An instance of the `RoleCollection` class representing the roles assigned to the user. If not provided, a new instance of `RoleCollection` will be created.
        - `claims` (list): A list of claims associated with the user. Default is an empty list.

        Returns:
        - None

        Attributes:
        - `claims` (list): A list of claims associated with the user.
        - `name` (str): The name of the user.
        - `access_token` (str): The access token for the user.
        - `id_token` (str): The ID token for the user.
        - `role_collection` (RoleCollection): An instance of the `RoleCollection` class representing the roles assigned to the user.
        """
        self.claims = claims or []
        self.name = name
        self.access_token = access_token
        self.id_token = id_token
        self.role_collection = role_collection or RoleCollection()

    def get_admin_roles(self):
        """This method retrieves the admin roles from the role collection.

        Returns:
        - A list of admin roles if they exist in the role collection.
        - None if no admin roles are found."""
        admin_roles = self.role_collection.get_rbac_by_type(settings.ADMIN_ROLE_NAME)
        return admin_roles[settings.ADMIN_ROLE_NAME] if admin_roles else admin_roles

    def is_plat_admin(self):
        """This method checks if the user has the platform admin role.

        Parameters:
        - None

        Returns:
        - True if the user has the platform admin role.
        - False otherwise."""
        for role in self.role_collection.roles:
            if role.role_type.lower() == settings.ADMIN_ROLE_NAME:
                return True
        return False

    def is_authorized(self, roles):
        """The `is_authorized` method checks if the user is authorized based on their roles.

        Parameters:
        - `roles` (list): A list of roles to check for authorization.

        Returns:
        - `True` if the user is authorized.
        - `False` if the user is not authorized.

        Note:
        - This method will always return `True` if the `FEATURE_RBAC_ENABLED` setting is disabled.
        - The user is considered authorized if they are a platform admin (`is_plat_admin()` returns `True`).
        - The user is considered authorized if they have all the roles specified in the `roles` parameter.
        """
        return (
            not settings.FEATURE_RBAC_ENABLED
            or self.is_plat_admin()
            or all((self.role_collection.get_rbac_by_type(role) for role in roles))
        )

    def __repr__(self):
        return f"User(id_token='{self.id_token}', name='{self.name}', access_token='{self.access_token}', role_collection={self.role_collection}, claims={self.claims})"

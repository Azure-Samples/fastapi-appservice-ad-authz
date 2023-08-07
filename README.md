This repository has sample implementation Azure RBAC control in API's using Azure AD groups for application running on Appservice.

## Pre-requisites

- Azure AD group with members
- Azure AD App Registration with API permissions
- Role created in Azure AD App Registration under App Roles (https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-add-app-roles-in-apps)
- Azure AD group to me mapped with Role created in App Registration (https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-add-app-roles-in-apps)

## Notes

This code makes few assumptions as below but can be modified to suit your needs.

### Assumptions

The Groups are created in format xxx-<env>-<role> where xxx can be anything (typically it would be team name or project name), env is the environment (dev, test, prod etc) and role
is the role name (contributor, reader, admin).

### Usage

After the setup in done and groups are in place one need to initialize the auth framework using init call. One can also set up custom role hierarchy if needed as below.

#### Step 1

```python 
# Initialize the role auth framework
role_heirarchy_spec = init()

# Define role hierarchy spec
admin_role = role_heirarchy_spec.create_role(settings.ADMIN_ROLE_NAME)
contributor_role = role_heirarchy_spec.create_role(settings.CONTRIBUTOR_ROLE_NAME)
reader_role = role_heirarchy_spec.create_role(settings.READER_ROLE_NAME)
admin_role.provide_implicit_permissions(contributor_role, reader_role)
contributor_role.provide_implicit_permissions(reader_role)
```

Here the admin role has implicit permissions on contributor and reader roles and contributor role has implicit permissions on reader role.

The code can be modified to have more complex role hierarchy as needed. We have used `reader` and `contributor` roles in our code but one can use any role names as needed.

#### Step 2

Using fastapi dependency injection mechanism indicate the role needed for the API as below.

```python
@app.get("/authenticated/messages")
async def get_messages(
        user: User = Depends(ValidateAndReturnUser(expected_roles = [settings.READER_ROLE_NAME])),
):
    """
    Returns a dictionary containing messages for the specified user. It uses dependency injection to get the user object. The RBAC validations are performed in ValidateAndReturnUser.

    Returns:
        dict: A dictionary containing messages for the specified user.
    """
    return {"messages": f"some messages for user {user.name}"}
```

`validate_and_return_user` is a dependency injection function which validates the user and returns the user object. The `expected_roles` parameter is used to indicate the roles
needed for the API. The `expected_roles` parameter is optional and if not provided the API will be accessible to all users.

`validate_and_return_user` returns user object which is of type `User` as below.

```python
class User:
    def __init__(
            self,
            id_token: str = (None,)
        name: str = (None,)

    access_token: str = (None,)
    role_collection = (None,)
    claims = (None,)
    ):
```

These properties can be used in code as required

### Important properties

FEATURE_RBAC_ENABLED: Defaults to false. This will enable API to derive roles based on group names if set to true. If set to false it will assume all users as admin user. The
environment in this case will be derived from the environment variable CP_AUTH_BYPASS_ENV.

CP_AUTH_BYPASS_ENV: Default value: "dev". Description: The environment name for bypassing CP authentication.

WEBSITE_AUTH_ENABLED: Default value: False. Description= Indicates whether website authentication is enabled. This will be auto set to true in Azure App Service when we configure
Azure AD authentication in App Service.

AZURE_CLIENT_ID: Default value: None. Description: The Azure client ID used for authentication and authorization purposes.

ADMIN_ROLE_NAME: Default value: "admin". Description: The name of the admin role.

CONTRIBUTOR_ROLE_NAME: Default value: "contributor". Description: The name of the contributor role.

READER_ROLE_NAME: Default value: "reader". Description: The name of the reader role.

CP_APP_NAME: Default value: "plat". Description: The name of the application. This is
particularly relevant in case of admin roles

VALID_ROLES:default value: Comma-separated string of ADMIN_ROLE_NAME CONTRIBUTOR_ROLE_NAME, and READER_ROLE_NAME. Description: The valid role names.

GROUP_NAME_SEPARATOR: Default value: "-". Description: The separator used in group names.

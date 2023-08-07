from fastapi import Depends, FastAPI

from auth import init
from auth.model.user import User
from auth.userProvider import ValidateAndReturnUser
from config import get_settings

app = FastAPI()

settings = get_settings()

# Initialize the role auth framework
role_heirarchy_spec = init()

# Define role hierarchy spec
admin_role = role_heirarchy_spec.create_role(settings.ADMIN_ROLE_NAME)
contributor_role = role_heirarchy_spec.create_role(settings.CONTRIBUTOR_ROLE_NAME)
reader_role = role_heirarchy_spec.create_role(settings.READER_ROLE_NAME)
admin_role.provide_implicit_permissions(contributor_role, reader_role)
contributor_role.provide_implicit_permissions(reader_role)


# API for unauthenticated messages
@app.get("/unauthenticated/messages")
async def get_system_info():
    # code to get system information
    return {"message": "Hello"}


@app.get("/authenticated/messages")
async def get_messages(
    user: User = Depends(ValidateAndReturnUser(expected_roles=[settings.READER_ROLE_NAME])),
):
    """
    Returns a dictionary containing messages for the specified user. It uses dependency injection to get the user object. The RBAC validations are performed in ValidateAndReturnUser.

    Returns:
        dict: A dictionary containing messages for the specified user.
    """
    return {"messages": f"some messages for user {user.name}"}


@app.post("/authenticated/message/{message}")
async def post_message(
    message: str,
    user: User = Depends(ValidateAndReturnUser(expected_roles=[settings.CONTRIBUTOR_ROLE_NAME])),
):
    # code to post message
    return {"message": f"{message} by user {user.name}"}


# API for health check

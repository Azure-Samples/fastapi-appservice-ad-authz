from functools import lru_cache
from os import environ
from typing import Optional

from pydantic.v1 import BaseSettings


class settings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    AZURE_TENANT_ID: Optional[str] = None
    WEBSITE_AUTH_ENABLED: bool = False  # https://learn.microsoft.com/en-us/azure/app-service/reference-app-settings?tabs=kudu%2Cpython#authentication--authorization
    AZURE_CLIENT_ID: Optional[str] = None
    ADMIN_ROLE_NAME: Optional[str] = "admin"
    CONTRIBUTOR_ROLE_NAME: Optional[str] = "contributor"
    READER_ROLE_NAME: Optional[str] = "reader"
    CP_APP_NAME = "plat"
    VALID_ROLES: str = f"{ADMIN_ROLE_NAME},{CONTRIBUTOR_ROLE_NAME},{READER_ROLE_NAME}"
    BYPASS_AUTH_FOR_BEHAVE_TESTING = False
    IS_ON_APP_SERVICE = "WEBSITE_SITE_NAME" in environ
    CP_AUTH_BYPASS_ENV = "dev"
    GROUP_NAME_SEPARATOR = "-"
    GROUP_PATTERN = (
        r"([a-zA-Z0-9_-]+)"
        + GROUP_NAME_SEPARATOR
        + "([a-zA-Z]+)"
        + GROUP_NAME_SEPARATOR
        + "([a-zA-Z]+)"
    )
    ADMIN_GROUP_PATTERN = (
        r"" + CP_APP_NAME + "-[a-zA-Z]+" + GROUP_NAME_SEPARATOR + "" + ADMIN_ROLE_NAME
    )
    GROUP_NODE_IN_DECODED_TOKEN = "groups"
    APP_SERVICE_ID_TOKEN_HEADER = "X-MS-TOKEN-AAD-ID-TOKEN"
    APP_SERVICE_ACCESS_TOKEN_HEADER = "X-MS-TOKEN-AAD-ACCESS-TOKEN"
    FEATURE_RBAC_ENABLED = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return settings()

import logging
import os

from config import get_settings

settings = get_settings()
settings.FEATURE_RBAC_ENABLED = True
# so that auth logic runs against fake tokens
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.DEBUG)


def before_all(context):
    context.deletion_map = {}
    settings.WEBSITE_AUTH_ENABLED = True
    settings.CP_AUTH_BYPASS_ENV = "dev"
    context.c_headers = {}

import logging
import os

from config import get_settings

settings = get_settings()
settings.FEATURE_RBAC_ENABLED = True
# so that auth logic runs against fake tokens
base_url_for_end_to_end = os.environ.get("BASE_URL_FOR_E2E")
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.DEBUG)


def before_all(context):
    context.deletion_map = {}
    settings.WEBSITE_AUTH_ENABLED = True
    settings.CP_AUTH_BYPASS_ENV = "dev"
    context.c_headers = {}

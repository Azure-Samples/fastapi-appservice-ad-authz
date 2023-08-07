import datetime
import os
from typing import Any
from unittest.mock import MagicMock

from behave import *
from jose import jwt
from starlette.testclient import TestClient

from api import app
from auth import init
from auth.exception import UnAuthorizedException
from auth.http.appservice import AppServiceBasedTokenProvider
from auth.jwttoken.token_service import DefaultTokenService
from auth.userProvider import ValidateAndReturnUser
from config import get_settings

settings = get_settings()

token_service = DefaultTokenService(token_provider=AppServiceBasedTokenProvider())


@step("I am part of below groups")
def setup_role(context):
    groups = []
    for row in context.table:
        groups.append(row["group"])

    payload_for_access_token = {
        "user_id": 123,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iss": "bdd-test",
        "audience": "bdd-test-execution",
        "kid": "secret_key",
    }

    # Define the secret key to sign the JWT token
    secret_key = "my_secret_key"
    # Create the JWT token
    headers = {"kid": secret_key}
    access_token = jwt.encode(
        payload_for_access_token, secret_key, algorithm="HS256", headers=headers
    )
    payload_for_id_token = payload_for_access_token
    payload_for_id_token["groups"] = groups
    payload_for_id_token["email"] = "bdd-buddy@invaliddomain.com"
    id_token = jwt.encode(
        payload_for_access_token, secret_key, algorithm="HS256", headers=headers
    )
    c_headers = {}
    c_headers[settings.APP_SERVICE_ACCESS_TOKEN_HEADER] = access_token
    c_headers[settings.APP_SERVICE_ID_TOKEN_HEADER] = id_token
    settings.WEBSITE_AUTH_ENABLED = True
    context.c_headers = c_headers


@step("I have access and id token")
def step_impl(context):
    assert (
        context.c_headers[settings.APP_SERVICE_ACCESS_TOKEN_HEADER] is not None
    ), "ERROR: ACCESS_TOKEN_HEADER not found"
    assert (
        context.c_headers[settings.APP_SERVICE_ID_TOKEN_HEADER] is not None
    ), "ERROR: ID_TOKEN_HEADER not found"


@then("User has {expected_roles} role against {environments} environment")
def step_impl(context, expected_roles, environments):
    def validate_and_assert(entitled_roles):
        assert len(entitled_roles) != 0, "ERROR: ENTITLED_ROLE not found"

    validate_roles_and_environment(
        context, expected_roles, environments, validate_and_assert
    )


def validate_roles_and_environment(context, expected_roles, environments, func):
    func_succeded = False
    u_user = ValidateAndReturnUser(expected_roles=expected_roles.split(","))
    mock_request = MagicMock()
    mock_request.headers = {
        settings.APP_SERVICE_ACCESS_TOKEN_HEADER: context.c_headers[
            settings.APP_SERVICE_ACCESS_TOKEN_HEADER
        ],
        settings.APP_SERVICE_ID_TOKEN_HEADER: context.c_headers[
            settings.APP_SERVICE_ID_TOKEN_HEADER
        ],
    }
    user = token_service.decode_and_check_authorization(
        u_user.expected_roles, request=mock_request
    )
    for expected_role in expected_roles.split(","):
        func_succeded = True
        for env in environments.split(","):
            entitled_roles = user.role_collection.get_rbac_by_env_and_type(
                env=env, role_type=expected_role
            )
            func(entitled_roles)
    return func_succeded


@then("User does not have {expected_roles} role against {environments} environment")
def step_impl(context, expected_roles, environments):
    def validate_and_assert(entitled_roles):
        assert (
            len(entitled_roles) == 0
        ), "ERROR: ENTITLED_ROLE found should have been missing"

    try:
        func_succeeded = validate_roles_and_environment(
            context, expected_roles, environments, validate_and_assert
        )
    except (
        UnAuthorizedException
    ) as e:  # In case if it is role mismatch the error will come here
        assert True
        return
    assert (
        func_succeeded
    ), "Error: Mismatched in roles"  # In case if it is environment mismatch. Environment is


@step("Role hierarchy is set up and auth framework is initialised")
def step_impl(context):
    role_heirarchy_spec = init()
    admin_role = role_heirarchy_spec.create_role(settings.ADMIN_ROLE_NAME)
    contributor_role = role_heirarchy_spec.create_role(settings.CONTRIBUTOR_ROLE_NAME)
    reader_role = role_heirarchy_spec.create_role(settings.READER_ROLE_NAME)
    admin_role.provide_implicit_permissions(contributor_role, reader_role)
    contributor_role.provide_implicit_permissions(reader_role)


@then("The response status code should be {status_code}")
def step_then(context, status_code):
    assert context.resp.status_code == int(status_code), "Expected {} got {}".format(
        status_code, context.resp.status_code
    )


def execute_get(client, c_headers, endpoint):
    resp = client.get(endpoint, headers=c_headers, cookies=None)
    return resp


def execute_post(client, c_headers, data, endpoint):
    if data is None:
        return client.post(endpoint, headers=c_headers, cookies=None)
    return client.post(endpoint, headers=c_headers, cookies=None, json=data)


@step("I hit the {endpoint} to get records")
def step_impl(context, endpoint):
    c_headers = context.c_headers
    response = run_in_client(execute_get, c_headers, endpoint)
    context.resp = response


def run_in_client(fn, *args):
    os.environ["no_proxy"] = "localhost"
    with TestClient(app, raise_server_exceptions=True) as client:
        return fn(client, *args)


def flatten_object(obj, prefix=""):
    flattened: dict[str | Any, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                flattened.update(flatten_object(value, f"{prefix}{key}."))
            else:
                flattened[f"{prefix}{key}"] = value
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            if isinstance(value, (dict, list)):
                flattened.update(flatten_object(value, f"{prefix}{index}."))
            else:
                flattened[f"{prefix}{index}"] = value
    else:
        flattened[prefix[:-1]] = obj
    return flattened


@step("The response should have below attribute")
def step_impl(context):
    flattened_object = flatten_object(context.resp.json())
    for row in context.table:
        value_in_object = flattened_object[row["attribute_name"]]
        assert value_in_object == row["value"], "Expected {}, got {}".format(
            row["value"], value_in_object
        )


def convert_row_to_dict(row):
    row_dict = {}
    for k, v in row.items():
        nested_keys = k.split(".")
        nested_dict = row_dict
        for nested_key in nested_keys[:-1]:
            nested_dict.setdefault(nested_key, {})
            nested_dict = nested_dict[nested_key]

        last_key = nested_keys[-1]
        if "," in v:
            temp_arr = []
            for element in v.split(","):
                if len(element.strip()) != 0:
                    temp_arr.append(element)
            nested_dict[last_key] = temp_arr
        else:
            nested_dict[last_key] = v

    return row_dict


def is_response_ok(status_code):
    return 200 <= status_code < 300


@when("I hit the {endpoint} of type post with below data")
def step_when(context, endpoint):
    if getattr(context, "resp", None) is not None:
        context.resp = None
    c_headers = context.c_headers
    resp = run_in_client(execute_post, c_headers, None, endpoint)
    context.resp = resp

from contextlib import nullcontext as does_not_raise

import aiohttp
import pytest
from fastapi import status

from tests.functional.core.settings import test_settings


@pytest.mark.parametrize(
    "query_data_login, query_data_main, query_body, expected_answer, expectation",
    [
        (
            {
                "email": "vasya@admin.ru",
                "hashed_password": "test_password",
            },
            {
                "role_name": "TestRoleName",
                "comment": "TestComment",
            },
            {
                "logout": True,
                "refresh_token": True,
                "history": True,
                "change_password": True,
                "create_role": False,
                "delete_role": False,
                "change_role": False,
                "get_roles": False,
                "set_role": False,
                "grab_role": False,
                "check_role": False,
            },
            {
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            },
            pytest.raises(aiohttp.ClientResponseError),
        )
    ],
)
@pytest.mark.asyncio
async def test_create_role(
    make_post_request,
    execute_raw_sql,
    query_data_login,
    query_data_main,
    query_body,
    expected_answer,
    expectation,
):
    url_create_user = test_settings.service_url + "/auth/signup"
    url_login = test_settings.service_url + "/auth/login/"
    url_logout = test_settings.service_url + "/auth/logout"
    url_create_role = test_settings.service_url + "/auth/roles/create"
    with expectation:
        _response_create_user, _status_create_user, _ = await make_post_request(
            url_create_user, query_data_login
        )

        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )

        _response_create, _status_create, _ = await make_post_request(
            url_create_role, query_data_main, _cookies_login, query_body
        )
        await make_post_request(url_logout, {}, _cookies_login)
        assert expected_answer["status"] == _status_create


@pytest.mark.parametrize(
    "query_data_login, query_data_main, query_body, expected_answer, expectation",
    [
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "role_name": "TestRoleName",
                "comment": "TestComment",
            },
            {
                "logout": True,
                "refresh_token": True,
                "history": True,
                "change_password": True,
                "create_role": False,
                "delete_role": False,
                "change_role": False,
                "get_roles": False,
                "set_role": False,
                "grab_role": False,
                "check_role": False,
            },
            {
                "status": status.HTTP_201_CREATED,
            },
            does_not_raise(),
        ),
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "role_name": "Admin",
                "comment": "TestComment",
            },
            [
                {
                    "logout": True,
                    "refresh_token": True,
                    "history": True,
                    "change_password": True,
                    "create_role": False,
                    "delete_role": True,
                    "change_role": False,
                    "get_roles": False,
                    "set_role": False,
                    "grab_role": False,
                    "check_role": False,
                }
            ],
            {
                "status": status.HTTP_409_CONFLICT,
                "detail": "Role is already exist",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_role_by_admin(
    make_post_request,
    redis_read_data,
    execute_raw_sql,
    query_data_login,
    query_data_main,
    query_body,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login/"
    url_logout = test_settings.service_url + "/auth/logout"
    url_create_role = test_settings.service_url + "/auth/roles/create"
    with expectation:
        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )
        _response_create, _status_create, _cookies_create = await make_post_request(
            url_create_role, query_data_main, _cookies_login, query_body
        )
        await make_post_request(url_logout, {}, _cookies_login)
        assert expected_answer["status"] == _status_create


@pytest.mark.parametrize(
    "query_data_login, expected_answer, expectation",
    [
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "status": status.HTTP_200_OK,
            },
            does_not_raise(),
        )
    ],
)
@pytest.mark.asyncio
async def test_read_role(
    make_post_request,
    make_get_request,
    execute_raw_sql,
    query_data_login,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login/"
    url_logout = test_settings.service_url + "/auth/logout"
    url_read_role = test_settings.service_url + "/auth/roles/read"
    with expectation:
        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )
        _response_read_role, _status_read_role, _ = await make_get_request(
            url_read_role, {}, _cookies_login
        )
        await make_post_request(url_logout, {}, _cookies_login)

        assert expected_answer["status"] == _status_read_role


@pytest.mark.parametrize(
    "query_data_login, query_data_main, query_body, expected_answer, expectation",
    [
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "role_name": "TestRoleName",
                "comment": "TestComment",
            },
            {
                "logout": True,
                "refresh_token": True,
                "history": True,
                "change_password": True,
                "create_role": False,
                "delete_role": False,
                "change_role": False,
                "get_roles": False,
                "set_role": False,
                "grab_role": False,
                "check_role": False,
            },
            {
                "status": status.HTTP_200_OK,
            },
            does_not_raise(),
        )
    ],
)
@pytest.mark.asyncio
async def test_update_role(
    make_post_request,
    make_put_request,
    execute_raw_sql,
    query_data_login,
    query_data_main,
    query_body,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login/"
    url_logout = test_settings.service_url + "/auth/logout"
    url_update_role = test_settings.service_url + "/auth/roles/update"
    with expectation:
        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )
        _response_update, _status_update, _ = await make_put_request(
            url_update_role, query_data_main, _cookies_login, query_body
        )

        await make_post_request(url_logout, {}, _cookies_login)
        assert expected_answer["status"] == _status_update


@pytest.mark.parametrize(
    "query_data_login, query_data_main, expected_answer, expectation",
    [
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "name": "TestRoleName",
            },
            {
                "status": status.HTTP_200_OK,
            },
            does_not_raise(),
        )
    ],
)
@pytest.mark.asyncio
async def test_delete_role(
    make_post_request,
    make_delete_request,
    execute_raw_sql,
    query_data_login,
    query_data_main,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login/"
    url_logout = test_settings.service_url + "/auth/logout"
    url_delete_role = test_settings.service_url + "/auth/roles/delete/"
    with expectation:
        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )
        _status_delete, _ = await make_delete_request(
            f"{url_delete_role}TestRoleName", {}, _cookies_login
        )
        await make_post_request(url_logout, {}, _cookies_login)
        assert expected_answer["status"] == _status_delete


@pytest.mark.parametrize(
    "query_data_login, query_data_main, expected_answer, expectation",
    [
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "user_email": "vasya@admin.ru",
                "role_name": "DefaultUser",
            },
            {"status": status.HTTP_409_CONFLICT, "detail": "This is actual role."},
            pytest.raises(aiohttp.ClientResponseError),
        )
    ],
)
@pytest.mark.asyncio
async def test_set_role(
    make_post_request,
    make_put_request,
    execute_raw_sql,
    query_data_login,
    query_data_main,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login/"
    url_logout = test_settings.service_url + "/auth/logout"
    url_set_role = test_settings.service_url + "/auth/roles/set"
    with expectation:
        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )
        _response_set, _status_set, _ = await make_post_request(
            url_set_role, query_data_main, _cookies_login
        )
        await make_post_request(url_logout, {}, _cookies_login)
        assert expected_answer["status"] == _status_set


@pytest.mark.parametrize(
    "query_data_login, query_data_main, expected_answer, expectation",
    [
        (
            {
                "email": "admin@admin.ru",
                "hashed_password": "admin",
            },
            {
                "user_email": "vasya@admin.ru",
                "role_name": "DefaultUser",
            },
            {"status": status.HTTP_200_OK},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_varify_role(
    make_post_request,
    make_put_request,
    execute_raw_sql,
    query_data_login,
    query_data_main,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login/"
    url_verify_role = test_settings.service_url + "/auth/roles/verify"
    with expectation:
        _response_login, _status_login, _cookies_login = await make_post_request(
            url_login, query_data_login
        )
        _response_verify, _status_verify, _ = await make_post_request(
            url_verify_role, query_data_main, _cookies_login
        )
        assert expected_answer["status"] == _status_verify

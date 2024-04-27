import asyncio
from contextlib import nullcontext as does_not_raise

import aiohttp
import pytest

from tests.functional.core.settings import test_settings
from fastapi import status


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {
                "email": "christian_bale@practix.ru",
                "user_name": "first_practix_user",
                "first_name": "practix_default_name",
                "last_name": "practix_last_name",
                "phone_number": "78005553535",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_201_CREATED},
            does_not_raise(),
        ),
        (
            {
                "email": "leonardo_dicaprio@practix.ru",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_201_CREATED},
            does_not_raise(),
        ),
        (
            {
                "email": "ryan_gosling",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_409_CONFLICT},
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {
                "email": "joseph_gordon_levitt@practix.ru",
                "hashed_password": "",
            },
            {"status": status.HTTP_422_UNPROCESSABLE_ENTITY},
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {
                "email": "christian_bale@practix.ru",
                "user_name": "christian_bale",
                "first_name": "practix_default_name",
                "last_name": "practix_last_name",
                "phone_number": "78005553535",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_409_CONFLICT},
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {
                "email": "christian_bale_fake@practix.ru",
                "user_name": "first_practix_user",
                "first_name": "practix_default_name",
                "last_name": "practix_last_name",
                "phone_number": "78005553535",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_409_CONFLICT},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_signup(
    make_post_request,
    execute_raw_sql,
    query_data,
    expected_answer,
    expectation,
):
    url = test_settings.service_url + "/auth/signup"
    with expectation:
        response, status, _ = await make_post_request(url, query_data)
        assert expected_answer["status"] == status
        assert query_data["email"] == response["email"]


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_200_OK},
            does_not_raise(),
        ),
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_200_OK},
            does_not_raise(),
        ),
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "wrong_password",
            },
            {"status": status.HTTP_409_CONFLICT},
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {
                "email": "christian_bale",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_409_CONFLICT},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_login(
    make_post_request,
    redis_read_data,
    execute_raw_sql,
    query_data,
    expected_answer,
    expectation,
):
    url = test_settings.service_url + "/auth/login"
    key = "refresh_tokens"
    with expectation:
        response, status, cookies = await make_post_request(url, query_data)
        response_redis = await redis_read_data(key)
        response_redis = [
            refresh_token.decode("UTF-8") for refresh_token in response_redis
        ]
        is_exist = cookies["refresh_token"].value in response_redis
        assert expected_answer["status"] == status
        assert is_exist


@pytest.mark.parametrize(
    "query_data_login, query_data_change, expected_answer, expectation",
    [
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "practix_password",
            },
            {
                "old_password ": "practix_password",
                "new_password ": "123",
            },
            {
                "status": status.HTTP_200_OK,
                "details": "Successfully changed password.",
            },
            does_not_raise(),
        ),
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "123",
            },
            {
                "old_password ": "123",
                "new_password ": "practix_password",
            },
            {
                "status": status.HTTP_200_OK,
                "details": "Successfully changed password.",
            },
            does_not_raise(),
        ),
    ],
)
@pytest.mark.asyncio
async def test_change_password(
    make_post_request,
    make_put_request,
    redis_read_data,
    execute_raw_sql,
    query_data_login,
    query_data_change,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login"
    url_change = test_settings.service_url + "/auth/change_password"
    url_logout = test_settings.service_url + "/auth/logout"
    with expectation:
        response_login, status_login, cookies_login = await make_post_request(
            url_login, query_data_login
        )
        response_change, status_change, cookies_change = await make_put_request(
            url_change, query_data_change, cookies_login
        )
        await make_post_request(
            url_logout,
            {},
            cookies_login,
        )
        assert expected_answer["status"] == status_change
        assert expected_answer["details"] == response_change["detail"]
        await asyncio.sleep(1)


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "practix_password",
            },
            {
                "status": status.HTTP_200_OK,
            },
            does_not_raise(),
        ),
    ],
)
@pytest.mark.asyncio
async def test_refresh(
    make_post_request,
    make_get_request,
    redis_read_data,
    execute_raw_sql,
    query_data,
    expected_answer,
    expectation,
):
    # TODO(MosyaginGrigorii): Добавить рандомные символы в токен
    url_login = test_settings.service_url + "/auth/login"
    url_change = test_settings.service_url + "/auth/refresh"
    with expectation:
        response_login, status_login, cookies_login = await make_post_request(
            url_login, query_data
        )
        response_change, status_change, cookies_change = await make_get_request(
            url_change, {}, cookies_login
        )
        assert expected_answer["status"] == status_change


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "practix_password",
            },
            {"status": status.HTTP_200_OK, "detail": "logout is successfully"},
            does_not_raise(),
        ),
    ],
)
@pytest.mark.asyncio
async def test_logout(
    make_post_request,
    redis_read_data,
    execute_raw_sql,
    query_data,
    expected_answer,
    expectation,
):
    # TODO(MosyaginGrigorii): Добавить рандомные символы в токен
    url_login = test_settings.service_url + "/auth/login"
    url_change = test_settings.service_url + "/auth/logout"
    with expectation:
        response_login, status_login, cookies_login = await make_post_request(
            url_login, query_data
        )
        response_change, status_change, cookies_change = await make_post_request(
            url_change, {}, cookies_login
        )
        assert expected_answer["status"] == status_change
        assert expected_answer["detail"] == response_change["detail"]


@pytest.mark.parametrize(
    "query_data, query_data_history, expected_answer, expectation",
    [
        (
            {
                "email": "christian_bale@practix.ru",
                "hashed_password": "practix_password",
            },
            {
                "page_size": 10,
                "page_number": 1,
            },
            {"status": status.HTTP_200_OK, "detail": "login successful"},
            does_not_raise(),
        ),
    ],
)
@pytest.mark.asyncio
async def test_history(
    make_post_request,
    make_get_request,
    redis_read_data,
    execute_raw_sql,
    query_data,
    query_data_history,
    expected_answer,
    expectation,
):
    url_login = test_settings.service_url + "/auth/login"
    url_history = test_settings.service_url + "/auth/history"
    with expectation:
        response_login, status_login, cookies_login = await make_post_request(
            url_login, query_data
        )
        response_history, status_history, cookies_history = await make_get_request(
            url_history, query_data_history, cookies_login
        )
        assert expected_answer["status"] == status_login
        assert expected_answer["status"] == status_history
        assert expected_answer["detail"] == response_login["detail"]
        assert len(response_history.get("response")) >= 1

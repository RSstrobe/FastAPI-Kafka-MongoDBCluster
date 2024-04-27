from http import HTTPStatus
import pytest
import aiohttp

from contextlib import nullcontext as does_not_raise

from tests.functional.core.settings import test_settings
from tests.functional.testdata.models import Genre
from tests.functional.testdata import es_data
from tests.functional.testdata import es_mapping

INDEX = "genres"
INDEX_MAPPING = es_mapping.GENRES_INDEX_MAPPING


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {
                "page_size": 10,
                "page_number": 1,
            },
            {"status": HTTPStatus.OK, "length": 10},
            does_not_raise(),
        ),
        (
            {"page_size": 101, "page_number": 1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"page_size": 1, "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"page_size": -1, "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"page_size": -1, "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_genres_main_page(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.genres_data, INDEX, Genre)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + "/api/v1/genres"
    key = f"genres_{query_data.get('page_size')}_{query_data.get('page_number')}"
    with expectation:
        response, status = await make_get_request(url, query_data)
        response_redis = await redis_read_data(key)
        assert status == expected_answer["status"]
        assert len(response.get("response")) == expected_answer["length"]
        assert len(response_redis.get("response")) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {"genre_id": es_data.genres_data[0]["id"]},
            {"status": HTTPStatus.OK, "name": "Western"},
            does_not_raise(),
        ),
        (
            {"genre_id": 123},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "name": "Nothing"},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_genres_by_id(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.genres_data, INDEX, Genre)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + f"/api/v1/genres/{query_data.get('genre_id')}"
    key = f"genres_id_{query_data.get('genre_id')}"
    with expectation:
        response, status = await make_get_request(url, {})
        response_redis = await redis_read_data(key)
        assert status == expected_answer["status"]
        assert response["name"] == expected_answer["name"]
        assert response_redis["name"] == expected_answer["name"]

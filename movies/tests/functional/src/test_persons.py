from http import HTTPStatus
import pytest
import aiohttp

from contextlib import nullcontext as does_not_raise

from tests.functional.core.settings import test_settings
from tests.functional.testdata.models import Person, Movie
from tests.functional.testdata import es_data
from tests.functional.testdata import es_mapping

INDEX = "persons"
INDEX_MAPPING = es_mapping.PERSONS_INDEX_MAPPING


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {"person_id": es_data.persons_data[0]["id"]},
            {"status": HTTPStatus.OK, "full_name": "Catherine Battistone"},
            does_not_raise(),
        ),
        (
            {"person_id": 123},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "full_name": "Nothing"},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_person_by_id(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.persons_data, INDEX, Person)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + f"/api/v1/persons/{query_data.get('person_id')}"
    key = f"persons_id_{query_data.get('person_id')}"
    with expectation:
        response, status = await make_get_request(url, {})
        response_redis = await redis_read_data(key)
        assert status == expected_answer["status"]
        assert response["full_name"] == expected_answer["full_name"]
        assert response_redis["full_name"] == expected_answer["full_name"]


@pytest.mark.parametrize(
    "person_id, query_data, expected_answer, expectation",
    [
        (
            es_data.persons_data[0]["id"],
            {"page_size": 10, "page_number": 1},
            {"status": HTTPStatus.OK, "length": 1},
            does_not_raise(),
        ),
        (
            123,
            {
                "page_size": 10,
                "page_number": 1,
                "genre": "04252541-9b71-4f35-987b-7328fbc19474",
            },
            {"status": HTTPStatus.OK, "length": 0},
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            es_data.persons_data[0]["id"],
            {"page_size": 101, "page_number": 1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            es_data.persons_data[0]["id"],
            {"page_size": 1, "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            es_data.persons_data[0]["id"],
            {"page_size": -1, "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            es_data.persons_data[0]["id"],
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
async def test_films_by_person_id(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    person_id,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.persons_data, INDEX, Person)
    bulk_query_films = generate_data(es_data.films_data_by_person, "movies", Movie)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)
    await es_write_data(bulk_query_films, "movies", es_mapping.MOVIES_INDEX_MAPPING)

    url = test_settings.service_url + f"/api/v1/persons/{person_id}/film"
    key = f"person_films_{person_id}_{query_data.get('page_size')}_{query_data.get('page_number')}"
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
            {
                "query": es_data.persons_data[0]["full_name"],
                "page_size": 10,
                "page_number": 1,
            },
            {"status": HTTPStatus.OK, "length": 10},
            does_not_raise(),
        ),
        (
            {"query": "non-valid-name", "page_size": 10, "page_number": 1},
            {"status": HTTPStatus.OK, "length": 0},
            does_not_raise(),
        ),
        (
            {"query": es_data.persons_data[0]["full_name"], "page_number": -1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "type_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"query": es_data.persons_data[0]["full_name"], "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "type_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"query": es_data.persons_data[0]["full_name"], "page_size": -1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "type_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"query": es_data.persons_data[0]["full_name"], "page_size": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "type_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_persons_search(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.persons_data, INDEX, Person)
    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + "/api/v1/personss/search"
    key = (
        f"persons_"
        f"{query_data.get('query')}_"
        f"{query_data.get('page_size')}_"
        f"{query_data.get('page_number')}"
    )

    with expectation:
        response, status = await make_get_request(url=url, query_data=query_data)
        response_redis = await redis_read_data(key)
        print(response_redis)
        assert status == expected_answer["status"]
        assert len(response.get("response")) == expected_answer["length"]
        assert len(response_redis["response"]) == expected_answer["length"]

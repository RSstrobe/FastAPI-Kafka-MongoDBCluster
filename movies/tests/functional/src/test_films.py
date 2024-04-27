from http import HTTPStatus
import pytest
import aiohttp

from contextlib import nullcontext as does_not_raise

from tests.functional.core.settings import test_settings
from tests.functional.testdata.models import Movie
from tests.functional.testdata import es_data
from tests.functional.testdata import es_mapping

INDEX = "movies"
INDEX_MAPPING = es_mapping.MOVIES_INDEX_MAPPING


# TODO(MosyaginGrigorii): Кажется уместным обернуть в scenario
@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {"page_size": 10, "page_number": 1, "sort": "imdb_rating"},
            {"status": HTTPStatus.OK, "length": 10},
            does_not_raise(),
        ),  # Проверка на корректность
        (
            {
                "page_size": 10,
                "page_number": 1,
                "sort": "imdb_rating",
                "genre": "04252541-9b71-4f35-987b-7328fbc19474",
            },
            {"status": HTTPStatus.OK, "length": 0},
            does_not_raise(),
        ),  # Несуществующий жанр
        (
            {
                "page_size": 10,
                "page_number": 1,
                "sort": "imdb_rating",
                "genre": "04252541-9b71-4f35-987b-7328fbc19473",
            },
            {"status": HTTPStatus.OK, "length": 10},
            does_not_raise(),
        ),  # Cуществующий жанр
        (
            {"page_size": 101, "page_number": 1, "sort": "imdb_rating"},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"page_size": 1, "page_number": 101, "sort": "imdb_rating"},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"page_size": -1, "page_number": 101, "sort": "imdb_rating"},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"page_size": -1, "page_number": 101, "sort": "imdb_rating"},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"genre": 123, "sort": "imdb_rating"},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "type_error.uuid",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_main_page(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.films_data, INDEX, Movie)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + "/api/v1/films"
    key = (
        f"films_"
        f"{query_data.get('sort')}_"
        f"{query_data.get('page_size')}_"
        f"{query_data.get('page_number')}_"
        f"{query_data.get('genre')}"
    )
    with expectation:
        response, status = await make_get_request(url, query_data)
        response_redis = await redis_read_data(key)
        assert status == expected_answer["status"]
        assert len(response.get("response")) == expected_answer["length"]
        # TODO(MosyaginGrigorii): Для честности лучше, конечно, assertListEqual из unittest
        assert len(response_redis.get("response")) == expected_answer["length"]


# TODO(MosyaginGrigorii): Вместо query_data можно просто film_id использоват
@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {"film_id": es_data.films_data[0]["id"]},
            {"status": HTTPStatus.OK, "length": 8},
            does_not_raise(),
        ),
        (
            {"film_id": 123},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 8},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_by_id(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.films_data, INDEX, Movie)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + f"/api/v1/films/{query_data.get('film_id')}"
    key = f"movies_id_{query_data.get('film_id')}"
    with expectation:
        response, status = await make_get_request(url, {})
        response_redis = await redis_read_data(key)
        assert status == expected_answer["status"]
        assert len(response) == expected_answer["length"]
        assert len(response_redis) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {"film_id": es_data.films_data[0]["id"], "page_size": 10, "page_number": 1},
            {"status": HTTPStatus.OK, "length": 8},
            does_not_raise(),
        ),
        (
            {
                "film_id": "1ef7a4e8-807c-4c63-aa43-701de733fff4",
                "page_size": 10,
                "page_number": 1,
            },
            {"status": HTTPStatus.OK, "length": 8},
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_by_similar_genre(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.films_data, INDEX, Movie)

    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + "/api/v1/films/films_by_similar_genre/"
    key = f"film_id_genres_{query_data.get('film_id')}"
    with expectation:
        response, status = await make_get_request(url, query_data)
        response_redis = await redis_read_data(key)
        assert status == expected_answer["status"]
        assert len(response.get("response")[0]) == expected_answer["length"]
        assert len(response_redis.get("response")[0]) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer, expectation",
    [
        (
            {
                "query": es_data.films_data[0]["title"],
                "page_size": 50,
                "page_number": 1,
            },
            {"status": HTTPStatus.OK, "length": 50},
            does_not_raise(),
        ),
        (
            {
                "query": es_data.films_data[0]["actors_names"][0],
                "page_size": 50,
                "page_number": 1,
            },
            {"status": HTTPStatus.OK, "length": 50},
            does_not_raise(),
        ),
        (
            {"query": "non-valid-film", "page_size": 50, "page_number": 1},
            {"status": HTTPStatus.OK, "length": 0},
            does_not_raise(),
        ),
        (
            {
                "query": es_data.films_data[0]["title"],
                "page_size": 10,
                "page_number": 1,
            },
            {"status": HTTPStatus.OK, "length": 10},
            does_not_raise(),
        ),
        (
            {"query": es_data.films_data[0]["title"], "page_number": -1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"query": es_data.films_data[0]["title"], "page_size": -1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_ge",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
        (
            {"query": es_data.films_data[0]["title"], "page_number": 101},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type_error": "value_error.number.not_lt",
            },
            pytest.raises(aiohttp.ClientResponseError),
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_search(
    generate_data,
    make_get_request,
    es_write_data,
    redis_read_data,
    query_data,
    expected_answer,
    expectation,
):
    bulk_query = generate_data(es_data.films_data, INDEX, Movie)
    await es_write_data(bulk_query, INDEX, INDEX_MAPPING)

    url = test_settings.service_url + "/api/v1/films/search/"
    key = (
        f"films_"
        f"{query_data.get('query')}_"
        f"{query_data.get('page_size')}_"
        f"{query_data.get('page_number')}"
    )

    with expectation:
        response, status = await make_get_request(url=url, query_data=query_data)
        response_redis = await redis_read_data(key)

        assert status == expected_answer["status"]
        assert len(response.get("response")) == expected_answer["length"]
        assert len(response_redis.get("response")) == expected_answer["length"]

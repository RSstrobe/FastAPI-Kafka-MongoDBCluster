from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi_limiter.depends import RateLimiter
from models.models import FilmFull, Page, Film
from models.request_models import (
    MainPageFilter,
    SearchByFilm,
    BaseModelPaginationFilter,
)
from services.film import FilmService, get_film_service

from helpers import access

router = APIRouter()


@router.get(
    "/films/",
    response_model=Page[Film],
    summary="Поиск популярных произведений",
    description="Информация по фильмам в зависимости от фильтрации",
    response_description="Список произведений, согласно заданному фильтру",
    tags=["Главная страница"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def popular_films(
    page_params: MainPageFilter = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> Page[Film] | list:
    response_films = await film_service.get_list_films_main_page(
        page_params.sort,
        page_params.page_size,
        page_params.page_number,
        page_params.genre,
    )
    if not response_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return response_films


@router.get(
    "/films/search",
    response_model=Page[Film],
    summary="Поиск кинопроизведений запросу",
    description="Поиск кинопроизведений по запросу",
    response_description="Список произведений, согласно заданному запросу",
    tags=["Поиск"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def search_films(
    query_params: SearchByFilm = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> Page[Film] | None:
    response_films = await film_service.search_films_by_query(
        query_params.query, query_params.page_size, query_params.page_number
    )
    if not response_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return response_films


@router.get(
    "/films/{film_id}",
    response_model=FilmFull,
    summary="Поиск кинопроизведения по id",
    description="Полная информация по фильму",
    response_description="Данные индекса Elasticsearch по id произведению",
    tags=["Страница фильма"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token
async def film_details(
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service),
    access_token: str = Cookie(None),
) -> FilmFull:
    response_film = await film_service.get_by_id(entity_id=film_id)
    if not response_film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return response_film


@router.get(
    "/films/films_by_similar_genre/",
    response_model=Page[Film],
    summary="Поиск кинопроизведений по схожести жанра",
    description="Полная информация по фильмам соответствующего жанра",
    response_description="Список произведений соответствующих жанру",
    tags=["Страница фильма"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token
async def films_by_similar_genre(
    film_id: UUID,
    query_params: BaseModelPaginationFilter = Depends(),
    film_service=Depends(get_film_service),
    access_token: str = Cookie(None),
) -> Page[Film] | None:
    response_film = await film_service.get_list_films_by_similar_genre(
        film_id, query_params.page_size, query_params.page_number
    )
    if not response_film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return response_film

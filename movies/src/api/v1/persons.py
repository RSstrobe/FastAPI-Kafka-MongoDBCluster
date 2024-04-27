from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi_limiter.depends import RateLimiter
from models.models import Person, Film, Page
from models.request_models import SearchByPerson, BaseModelPaginationFilter
from services.person import PersonService, get_person_service

from helpers import access

router = APIRouter()


@router.get(
    "/persons/{person_id}",
    response_model=Person,
    summary="Информация о персоне",
    description="Информация о персоне",
    response_description="Информация о персоне",
    tags=["Страница персонажа"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token
async def persons_list(
    person_id: UUID,
    genre_service: PersonService = Depends(get_person_service),
) -> Person:
    response_person = await genre_service.get_by_id(entity_id=person_id)
    if not response_person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return response_person


@router.get(
    "/personss/search",
    response_model=Page[Person],
    summary="Поиск по персонe",
    description="Поиск по персоне",
    response_description="Список персон",
    tags=["Поиск"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token
async def search_persons(
    query_params: SearchByPerson = Depends(),
    person_service: PersonService = Depends(get_person_service),
    access_token: str = Cookie(None),
) -> Page[Person] | None:
    response_persons = await person_service.search_persons_by_query(
        query_params.query, query_params.page_size, query_params.page_number
    )
    if not response_persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return response_persons


@router.get(
    "/persons/{person_id}/film",
    response_model=Page[Film],
    description="Поиск по персоне",
    response_description="Список фильмов",
    tags=["Страница персонажа"],
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token
async def films_by_person(
    person_id: UUID,
    query_params: BaseModelPaginationFilter = Depends(),
    person_service: PersonService = Depends(get_person_service),
    access_token: str = Cookie(None),
) -> Page[Film] | None:
    response_film = await person_service.get_list_films_by_person(
        person_id, query_params.page_size, query_params.page_number
    )
    if not response_film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return response_film

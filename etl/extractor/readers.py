"""
Модуль с методами для чтения данных из Postgres.
"""
import datetime
from typing import List, Tuple, Union, Any, Iterator
from uuid import UUID

from psycopg2.extras import RealDictCursor, RealDictRow


def get_modified_common_ids(
    cursor: RealDictCursor,
    schema: str,
    db_name: str,
    ref_datetime: datetime.datetime,
    previous_id: str = "",
    limit_rows: int = 200,
) -> Iterator[Union[List[Any], Tuple[Any, Tuple[UUID, ...]]]]:
    """
    Метод для получения обновленных id.

    :param cursor: курсор
    :param schema: схема БД
    :param db_name: таблица БД
    :param ref_datetime: опорное значение времени, после которого считаем записи измененными
    :param previous_id: предыдущее значение id
    :param limit_rows: ограничение на количество выводимых строк

    :yield: генератор списка словарей с id и временем изменения записи
    """

    additional_query: str = ""

    if previous_id:
        additional_query = f"and id > '{previous_id}'"

    query = f"""
        select *
        from {schema}.{db_name}
        where modified > %(ref_datetime)s
        {additional_query}
        order by id
        limit {limit_rows};;
    """

    mogrify_query = cursor.mogrify(
        query, {"ref_datetime": ref_datetime, "limit_rows": limit_rows}
    )

    cursor.execute(mogrify_query)

    res_rows = cursor.fetchall()

    prepared_ids = tuple(UUID(row["id"]) for row in res_rows)

    yield res_rows, prepared_ids


def get_modified_person_ids_from_film_work(
    cursor: RealDictCursor,
    ref_datetime: datetime.datetime,
    previous_id: str = "",
    limit_rows: int = 200,
) -> Iterator[Union[List[Any], Tuple[Any, Tuple[UUID, ...]]]]:
    """
    Метод для получения обновленных id.

    :param cursor: курсор
    :param schema: схема БД
    :param db_name: таблица БД
    :param ref_datetime: опорное значение времени, после которого считаем записи измененными
    :param previous_id: предыдущее значение id
    :param limit_rows: ограничение на количество выводимых строк

    :yield: генератор списка словарей с id и временем изменения записи
    """

    additional_query: str = ""

    if previous_id:
        additional_query = f"and pfw.person_id > '{previous_id}'"

    query = f"""
        select
            pfw.person_id as id
        from content.film_work fw
        left join content.person_film_work pfw on fw.id = pfw.film_work_id
        where fw.modified >= %(ref_datetime)s {additional_query}
        order by id
        limit {limit_rows};
    """

    mogrify_query = cursor.mogrify(
        query, {"ref_datetime": ref_datetime, "limit_rows": limit_rows}
    )

    cursor.execute(mogrify_query)

    res_rows = cursor.fetchall()

    prepared_ids = tuple(UUID(row["id"]) for row in res_rows)

    yield res_rows, prepared_ids


def get_modified_film_work_ids(
    cursor: RealDictCursor,
    schema: str,
    db_name: str,
    entity_id_name: str,
    ids_to_find: Tuple[UUID, ...],
    previous_id: str = "",
    limit_rows: int = 200,
) -> Union[List[Any], Tuple[Any, Tuple[UUID, ...]]]:
    """
    Метод для пролучения id произведений по измененным жанрам или персоналиям.

    :param cursor: курсор
    :param schema: схема БД
    :param db_name: таблица БД (person_film_work, genre_film_work)
    :param entity_id_name: имя сущности
    :param ids_to_find: кортеж с id персоналий или жанров, по которым необходимо найти произведения
    :param previous_id: предыдущее значение id
    :param limit_rows: ограничение на количество выводимых строк

    :return: списо словарей с id и временем изменения записи
    """

    if not ids_to_find:
        return []

    additional_query: str = ""

    if previous_id:
        additional_query = f"and fw.id > '{previous_id}'"

    query = f"""
            select fw.id, fw.modified
            from content.film_work fw
            left join {schema}.{db_name} pfw on pfw.film_work_id = fw.id
            where pfw.{entity_id_name} in {ids_to_find}
            {additional_query}
            order by fw.id
            limit {limit_rows};
        """

    cursor.execute(query)

    mogrify_query = cursor.mogrify(query, {"limit_rows": limit_rows})

    cursor.execute(mogrify_query)

    res_rows = cursor.fetchall()

    prepared_ids = tuple(UUID(row["id"]) for row in res_rows)

    return res_rows, prepared_ids


def get_full_data(
    cursor: RealDictCursor, ids_to_find: Tuple[UUID, ...]
) -> Union[List[Any], List[RealDictRow]]:
    """
    Метод для получения недостающей информации, необходимой для трансфера данных в ES.

    :param cursor: курсор
    :param ids_to_find: кортеж с id, по которым необходимо собрать информацию

    :return: список списков с недостающей информацией
        [
            RealDictRow(
                [
                    ('fw_id', '317df96f-2cbc-48fd-98ba-16a94cac68a0'),
                    ('title', 'Phantasy Star'),
                    ('description',
                    'After her older brother dies, young Alis driven by his last words races to save her planet and solar system from a force of evil.'),
                    ('rating', 8.5),
                    ('type', 'movie'),
                    ('created',
                    datetime.datetime(2021, 6, 16, 20, 14, 9, 249329, tzinfo=datetime.timezone.utc)),
                    ('modified',
                    datetime.datetime(2021, 6, 16, 20, 14, 9, 249344, tzinfo=datetime.timezone.utc)),
                    ('genres', ['Action', 'Adventure', 'Animation']),
                    (
                        'director',
                        [
                            {
                                'created': '2021-06-16T20:14:09.434161+00:00',
                                'modified': '2021-06-16T20:14:09.434177+00:00',
                                'id': '07ced051-0b0c-4f76-8980-05c3167d8e2a',
                                'full_name': 'Yuji Naka'
                            }
                        ]
                    ),
                    ('actors', None),
                    (
                        'writers',
                        [
                            {
                                'created': '2021-06-16T20:14:09.428007+00:00',
                                'modified': '2021-06-16T20:14:09.428023+00:00',
                                'id': '84b79bc9-4ca6-4b45-8eab-a016a5868a2d',
                                'full_name': 'Rieko Kodama'
                            },
                        ],
                ],
            ),
        ]
    """

    if not ids_to_find:
        return []

    query = f"""
        select
            fw.id as fw_id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            json_agg(distinct g.*) as genres,
            json_agg(distinct p.full_name) filter(where pfw.role = 'actor') as actors_names,
            json_agg(distinct p.full_name) filter(where pfw.role = 'writer') as writers_names,
            json_agg(distinct p.*) filter(where pfw.role = 'director') as director,
            json_agg(distinct p.*) filter(where pfw.role = 'actor') as actors,
            json_agg(distinct p.*) filter(where pfw.role = 'writer') as writers
        from content.film_work fw
        left join content.person_film_work pfw on pfw.film_work_id = fw.id
        left join content.person p on p.id = pfw.person_id
        left join content.genre_film_work gfw on gfw.film_work_id = fw.id
        left join content.genre g on g.id = gfw.genre_id
        where fw.id in {ids_to_find}
        group by fw.id;
    """

    cursor.execute(query)

    res_rows = cursor.fetchall()

    return res_rows


def get_full_data_persons(
    cursor: RealDictCursor, ids_to_find: Tuple[UUID, ...]
) -> Union[List[Any], List[RealDictRow]]:
    """
    Метод для получения недостающей информации, необходимой для трансфера данных в ES.

    :param cursor: курсор
    :param ids_to_find: кортеж с id, по которым необходимо собрать информацию

    :return: список списков с недостающей информацией
    """
    if not ids_to_find:
        return []

    query = f"""
        with pfd as (
            select
                p.id as id,
                p.full_name as full_name,
                fw.id as fw_id,
                array_agg(pfw.role) as role
            from content.person p
            left join content.person_film_work pfw on p.id = pfw.person_id
            left join content.film_work fw on pfw.film_work_id = fw.id
            where p.id in {ids_to_find}
            group by p.id, p.full_name, fw.id
        )
        select
            pfd.id,
            pfd.full_name,
            json_object_agg(pfd.fw_id, pfd.role) as films
        from pfd
        group by pfd.id, pfd.full_name
    """

    cursor.execute(query)

    res_rows = cursor.fetchall()

    return res_rows

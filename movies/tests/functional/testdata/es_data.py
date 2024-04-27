"""A module for generate test data for ElasticSearch."""

import datetime
import uuid

films_data = [
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": 8.5,
        "genre": [
            {"id": "04252541-9b71-4f35-987b-7328fbc19473", "name": "Action"},
            {"id": "5c414c89-9516-4438-b47d-e3b226c81dce", "name": "Scifi"},
        ],
        "title": "The Star",
        "description": "New World",
        "director": [
            {"id": "d5529121-aefb-474c-a08e-f2a96b40fb10", "full_name": "Stan"}
        ],
        "actors_names": ["Ann", "Bob"],
        "writers_names": ["Ben", "Howard"],
        "actors": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "full_name": "Ann"},
            {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "full_name": "Bob"},
        ],
        "writers": [
            {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "full_name": "Ben"},
            {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "full_name": "Howard"},
        ],
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
        "film_work_type": "movie",
    }
    for _ in range(60)
]

genres_data = [
    {
        "id": "0b105f87-e0a5-45dc-8ce7-f8632088f390",
        "name": "Western",
        "description": "",
    },
    {
        "id": "120a21cf-9097-479e-904a-13dd7198c1dd",
        "name": "Adventure",
        "description": "",
    },
    {"id": "1cacff68-643e-4ddd-8f57-84b62538081a", "name": "Drama", "description": ""},
    {
        "id": "237fd1e4-c98e-454e-aa13-8a13fb7547b5",
        "name": "Romance",
        "description": "",
    },
    {"id": "2f89e116-4827-4ff4-853c-b6e058f71e31", "name": "Sport", "description": ""},
    {
        "id": "31cabbb5-6389-45c6-9b48-f7f173f6c40f",
        "name": "Talk-Show",
        "description": "",
    },
    {"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action", "description": ""},
    {
        "id": "526769d7-df18-4661-9aa6-49ed24e9dfd8",
        "name": "Thriller",
        "description": "",
    },
    {"id": "5373d043-3f41-4ea8-9947-4b746c601bbd", "name": "Comedy", "description": ""},
    {"id": "55c723c1-6d90-4a04-a44b-e9792040251a", "name": "Family", "description": ""},
]

persons_data = [
    {
        "id": str(uuid.uuid4()),
        "full_name": "Catherine Battistone",
        "films": [{"id": "ec07f763-f2a1-49b5-b137-2e31f64cb090", "roles": ["actor"]}],
    }
    for _ in range(60)
]

films_data_by_person = [
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": 8.5,
        "genre": [
            {"id": "04252541-9b71-4f35-987b-7328fbc19473", "name": "Action"},
            {"id": "5c414c89-9516-4438-b47d-e3b226c81dce", "name": "Scifi"},
        ],
        "title": "The Star",
        "description": "New World",
        "director": [
            {"id": "d5529121-aefb-474c-a08e-f2a96b40fb10", "full_name": "Stan"}
        ],
        "actors_names": ["Ann", "Bob"],
        "writers_names": ["Ben", "Howard"],
        "actors": [
            {"id": row["id"], "full_name": "Ann"},
            {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "full_name": "Bob"},
        ],
        "writers": [
            {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "full_name": "Ben"},
            {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "full_name": "Howard"},
        ],
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
        "film_work_type": "movie",
    }
    for row in persons_data
]

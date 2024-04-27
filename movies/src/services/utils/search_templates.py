from uuid import UUID


class SearchTemplates:
    @staticmethod
    def genre_templates() -> dict:
        query = {
            "query": {"query_string": {"query": "*"}},
        }
        return query

    @staticmethod
    def persons_search_template(search_query: str) -> dict:
        query = {
            "query": {
                "multi_match": {
                    "query": search_query,
                    "fields": ["full_name"],
                }
            },
        }
        return query

    @staticmethod
    def search_films_by_person_id(person_id: UUID) -> dict:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"terms": {"directors.id": [str(person_id)]}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"terms": {"writers.id": [str(person_id)]}},
                            }
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"terms": {"actors.id": [str(person_id)]}},
                            }
                        },
                    ]
                }
            },
        }
        return query

    @staticmethod
    def films_by_genre_ids(genre_ids: list[UUID]) -> dict:
        query = {"query": {"query_string": {"query": "*"}}}
        if genre_ids:
            genres_ids: list[str] = [str(row) for row in genre_ids]
            query["query"] = {
                "bool": {
                    "must": [
                        {
                            "nested": {
                                "path": "genres",
                                "query": {"terms": {"genres.id": genres_ids}},
                            }
                        }
                    ]
                }
            }
        return query

    @staticmethod
    def films_search_template(search_query: str) -> dict:
        query = {
            "query": {
                "multi_match": {
                    "query": search_query,
                    "fields": [
                        "title",
                        "description",
                        "actors_names",
                        "writers_names",
                        "genres.name",
                        "directors.full_name",
                    ],
                }
            },
        }
        return query

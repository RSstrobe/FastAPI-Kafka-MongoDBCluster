import math


class SearchBodyCreator:
    @staticmethod
    def get_total_pages(elastic_response: dict, page_size: int) -> int:
        total_documents = elastic_response["hits"]["total"]["value"]
        total_pages = math.ceil(total_documents / page_size)
        return total_pages

    @staticmethod
    def get_pagination_parameters(
        page_size: int, page_number: int
    ) -> tuple[int, int] | None:
        offset = (page_number - 1) * page_size
        limit = offset + page_size
        return offset, limit

    @staticmethod
    def add_sort(search_body: dict, sort_query: str) -> dict:
        if sort_query[0] == "-":
            order_field = sort_query[1:]
            order_type = "desc"
        else:
            order_field = sort_query.replace("+", "")
            order_type = "asc"
        search_body["sort"] = [{order_field: {"order": order_type}}]
        return search_body

    def add_pagination(self, query: dict, page_size: int, page_number: int) -> dict:
        offset, limit = self.get_pagination_parameters(page_size, page_number)
        query["from"] = offset
        query["size"] = limit
        return query

    def create_search_body(
        self, search_template: dict, sort_query: str, page_size: int, page_number: int
    ) -> dict:

        search_body = self.add_sort(search_body=search_template, sort_query=sort_query)
        search_body = self.add_pagination(
            query=search_body, page_size=page_size, page_number=page_number
        )

        return search_body

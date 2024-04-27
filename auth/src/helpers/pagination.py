def get_pagination_parameters(
    page_size: int, page_number: int
) -> tuple[int, int] | None:
    offset = (page_number - 1) * page_size
    limit = offset + page_size
    return offset, limit


def get_total_pages(total_records: int, page_size: int) -> int:
    return (total_records + page_size - 1) // page_size

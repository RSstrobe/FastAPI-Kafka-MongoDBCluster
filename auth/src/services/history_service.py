import uuid
from fastapi import Depends

from helpers.pagination import get_total_pages
from repositories.auth_history_repository import (
    AuthHistoryRepository,
    get_db_history_client,
)
from schemas import histories
from schemas.base import Page
from .base_service import BaseService


class HistoryService(BaseService):
    def __init__(self, database_client: AuthHistoryRepository):
        self.database_client = database_client

    async def get(self, user_id: str, history_data: histories.HistoryRequestSchema):
        total_records = await self.database_client.get_total_records(user_id)
        total_pages = get_total_pages(total_records, history_data.page_size)
        list_history = await self.database_client.get_auth_history(
            user_id, history_data
        )
        response = Page(
            response=list_history,
            page=history_data.page_number,
            page_size=history_data.page_size,
            total_pages=total_pages,
        )
        return response

    async def create(self, user_id, device_id) -> None:
        _session = await self.database_client.add_login_history(
            user_id=user_id,
            device_id=device_id,
        )
        return _session

    async def delete(self, *args, **kwargs):
        pass

    async def update(self, session_id: uuid.UUID):
        await self.database_client.add_logout_history(session_id)


def get_history_service(
    database_client: AuthHistoryRepository = Depends(get_db_history_client),
) -> HistoryService:
    return HistoryService(database_client=database_client)

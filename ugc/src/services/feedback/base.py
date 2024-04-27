import math

from schemas.base import Page
from repositories.mongo_repositorty import MongoBeanieRepository
from core.exceptions import EntityExistException, EntityNotExistException


class BaseFeedbackService(MongoBeanieRepository):
    def __init__(self, client, collection, response_class, search_param: str):
        super().__init__(client=client, collection=collection)
        self.response_class = response_class
        self.search_param = search_param

    @staticmethod
    def is_delete_document(document: dict):
        return document.get("is_delete")

    async def is_object_exists(self, document: dict):
        doc = {
            "user_id": document["user_id"],
            self.search_param: document[self.search_param],
        }
        response = await self.read(
            document=doc, sort_by="dt", skip=0, limit=1, sort_method=-1
        )
        return response

    async def get_pagination_settings(self, document: dict, pagination_settings: dict):
        if "page_size" not in pagination_settings:
            page_size = 50
        else:
            page_size = pagination_settings["page_size"]
        if "page_number" not in pagination_settings:
            page_number = 1
        else:
            page_number = pagination_settings["page_number"]

        total_documents = await self.count(document=document)
        total_pages = math.ceil(total_documents / page_size)

        return page_size, page_number, total_pages

    async def get_with_pagination(self, document: dict, pagination_settings: dict):
        page_size, page_number, total_pages = await self.get_pagination_settings(
            document=document, pagination_settings=pagination_settings
        )

        res = await self.read(
            document=document,
            skip=(page_number - 1) * page_size,
            limit=page_size * page_number,
        )

        list_bookmarks = [self.response_class(**doc) for doc in res]

        response = Page(
            response=list_bookmarks,
            page=page_number,
            page_size=page_size,
            total_pages=total_pages,
        )
        return response

    async def delete_object(self, document: dict):
        objects = await self.is_object_exists(document=document)

        if not objects or self.is_delete_document(objects[0]):
            raise EntityNotExistException

        filter_data = {
            "user_id": document["user_id"],
            self.search_param: document[self.search_param],
        }
        document["is_delete"] = True
        await self.update(filter_data=filter_data, update_data=document)
        return None

    async def save_object(self, document: dict):
        response = await self.is_object_exists(document=document)

        if not response:
            await self.create(document=document)
            return

        if not self.is_delete_document(response[0]):
            raise EntityExistException

        filter_data = {
            "user_id": document["user_id"],
            self.search_param: document[self.search_param],
        }
        document["is_delete"] = False

        await self.update(filter_data=filter_data, update_data=document)

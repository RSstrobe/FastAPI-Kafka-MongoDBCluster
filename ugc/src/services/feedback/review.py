from functools import lru_cache

from fast_depends import inject, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from .base import BaseFeedbackService
from db.mongo import get_mongo_client
from schemas.response import ReviewSchema


class ReviewService(BaseFeedbackService):
    def __init__(self, client):
        super().__init__(
            client=client,
            collection="review",
            response_class=ReviewSchema,
            search_param="movie_id",
        )


@lru_cache()
@inject
def get_review_service(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> ReviewService:
    return ReviewService(mongo_client)

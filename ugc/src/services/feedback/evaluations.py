from functools import lru_cache

from fast_depends import inject, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from .base import BaseFeedbackService
from db.mongo import get_mongo_client
from schemas.response import EvaluationResponse


class EvaluationService(BaseFeedbackService):
    def __init__(self, client):
        super().__init__(
            client=client,
            collection="evaluation",
            response_class=EvaluationResponse,
            search_param="review_id",
        )


@lru_cache()
@inject
def get_evaluation_service(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> EvaluationService:
    return EvaluationService(mongo_client)

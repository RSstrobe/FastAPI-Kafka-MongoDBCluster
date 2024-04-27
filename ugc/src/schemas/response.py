from uuid import UUID
from datetime import datetime
from schemas.base import BaseSchema


class ReviewSchema(BaseSchema):
    user_id: UUID
    score: int
    text: str
    dt: datetime


class BookmarkResponse(BaseSchema):
    user_id: UUID
    movie_id: UUID


class EvaluationResponse(BaseSchema):
    user_id: UUID
    score: int
    dt: datetime

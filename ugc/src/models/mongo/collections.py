from uuid import uuid4
import datetime
from enum import IntEnum

from beanie import Document, Indexed
from pydantic import Field


class ReviewScore(IntEnum):
    LIKE = 1
    DISLIKE = -1


class Review(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Indexed(str)
    movie_id: str
    score: int
    evaluation_sum: int = Field(default=0)
    text: str = Field(default=None)
    is_delete: bool = Field(default=False)
    dt: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    class Settings:
        name = "review"
        use_state_management = True


class Evaluation(Document):
    user_id: str
    review_id: Indexed(str)
    score: ReviewScore
    is_delete: bool = Field(default=False)
    dt: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    class Settings:
        name = "evaluation"
        use_state_management = True


class Bookmark(Document):
    user_id: Indexed(str)
    movie_id: str
    is_delete: bool = Field(default=False)
    dt: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    class Settings:
        name = "bookmark"
        use_state_management = True

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class Review(BaseModel):
    id: UUID = Field(comment="Идентификатор оценки")
    user_id: UUID = Field(comment="Идентификатор пользователя")
    movie_id: UUID = Field(comment="Идентификатор фильма")
    score: int = Field(comment="Полезность отзыва")
    text: str = Field(comment="Тест отзыва")

    is_delete: bool = Field(comment="Пометка об удалении")
    dt: datetime = Field(comment='Дата события', alias='event_dt', validation_alias='dt')

    @classmethod
    def get_field_names(cls):
        fields_data = cls.model_fields

        fields_names = []
        for basic_field_name, field_data in fields_data.items():
            if alias_name := field_data.alias:
                fields_names.append(alias_name)
            else:
                fields_names.append(basic_field_name)

        return fields_names


class Bookmark(BaseModel):
    user_id: UUID = Field(comment="Идентификатор пользователя")
    movie_id: UUID = Field(comment="Идентификатор фильма")

    is_delete: bool = Field(comment="Пометка об удалении")
    dt: datetime = Field(comment='Дата события', alias='event_dt', validation_alias='dt')

    @classmethod
    def get_field_names(cls):
        fields_data = cls.model_fields

        fields_names = []
        for basic_field_name, field_data in fields_data.items():
            if alias_name := field_data.alias:
                fields_names.append(alias_name)
            else:
                fields_names.append(basic_field_name)

        return fields_names


class ReviewRating(BaseModel):
    user_id: UUID = Field(comment="Идентификатор пользователя")
    review_id: UUID = Field(comment="Идентификатор отзыва")
    score: int = Field(comment="Полезность отзыва")

    is_delete: bool = Field(comment="Пометка об удалении")
    dt: datetime = Field(comment='Дата события', alias='event_dt', validation_alias='dt')

    @classmethod
    def get_field_names(cls):
        fields_data = cls.model_fields

        fields_names = []
        for basic_field_name, field_data in fields_data.items():
            if alias_name := field_data.alias:
                fields_names.append(alias_name)
            else:
                fields_names.append(basic_field_name)

        return fields_names


# class Review(BaseModel):
#     user_id: UUID = Field(comment="Идентификатор пользователя")
#     movie_id: UUID = Field(comment="Идентификатор фильма")
#     score: int = Field(comment="Полезность отзыва")
#     text: str = Field(comment="Тест отзыва")
#     is_delete: bool = Field(comment="Пометка об удалении")
#     dt: datetime = Field(comment='Дата события', alias='event_dt', validation_alias='dt')

#     @classmethod
#     def get_field_names(cls):
#         fields_data = cls.model_fields

#         fields_names = []
#         for basic_field_name, field_data in fields_data.items():
#             if alias_name := field_data.alias:
#                 fields_names.append(alias_name)
#             else:
#                 fields_names.append(basic_field_name)

#         return fields_names


# class Bookmark(BaseModel):
#     user_id: UUID = Field(comment="Идентификатор пользователя")
#     movie_id: UUID = Field(comment="Идентификатор фильма")
#     is_delete: bool = Field(comment="Пометка об удалении")
#     dt: datetime = Field(comment='Дата события', alias='event_dt', validation_alias='dt')

#     @classmethod
#     def get_field_names(cls):
#         fields_data = cls.model_fields

#         fields_names = []
#         for basic_field_name, field_data in fields_data.items():
#             if alias_name := field_data.alias:
#                 fields_names.append(alias_name)
#             else:
#                 fields_names.append(basic_field_name)

#         return fields_names


# class ReviewRating(BaseModel):
#     user_id: UUID = Field(comment="Идентификатор пользователя")
#     review_id: UUID = Field(comment="Идентификатор отзыва")
#     score: int = Field(comment="Полезность отзыва")
#     is_delete: bool = Field(comment="Пометка об удалении")
#     dt: datetime = Field(comment='Дата события', alias='event_dt', validation_alias='dt')

#     @classmethod
#     def get_field_names(cls):
#         fields_data = cls.model_fields

#         fields_names = []
#         for basic_field_name, field_data in fields_data.items():
#             if alias_name := field_data.alias:
#                 fields_names.append(alias_name)
#             else:
#                 fields_names.append(basic_field_name)

#         return fields_names
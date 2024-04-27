from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, str_256, uuidpk, str_50


class SocialNetworksNames(Enum):
    yandex = "yandex"
    vk = "vk"
    google = "google"


class SocialNetworks(Base):
    def __repr__(self):
        return f"<SocialAccount {self.social_networks_name}:{self.user_id}>"

    __tablename__ = "social_networks"

    id: Mapped[uuidpk]
    user_id: Mapped[uuidpk] = mapped_column(
        ForeignKey(
            column="user_data.id",
            ondelete="CASCADE",
            name="mix_social_networks_user_id_fkey",
        ),
        comment="User id",
        nullable=False,
    )
    social_network_id: Mapped[str_50] = mapped_column(
        comment="Social network user id",
        nullable=False,
    )
    social_network_email: Mapped[str_256] = mapped_column(
        comment="Social network user email address",
        nullable=False,
    )
    social_networks_name: Mapped[SocialNetworksNames] = mapped_column(
        comment="Social networks names",
        nullable=False,
    )

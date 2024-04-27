from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """Base abstract class for all getting repositories."""

    def __init__(self, connection: any = None):
        """
        :param connection: connector to database.
        """
        self.connection = connection

    @abstractmethod
    async def get(self, *args, **kwargs):
        """Get data from database."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close async client connection."""
        if self.connection:
            await self.connection.close()


class MixinSearchingRepository(BaseRepository, ABC):
    """Base abstract class for searching repositories."""

    @abstractmethod
    async def search(self, *args, **kwargs):
        """Search data in database."""
        raise NotImplementedError


class MixinWriteRepository(BaseRepository, ABC):
    """Base abstract class for writing repositories."""

    @abstractmethod
    async def set(self, *args, **kwargs):
        """Function for execute set operations."""
        raise NotImplementedError


class MixinSaveRepository(BaseRepository, ABC):
    """Base abstract class for save repositories."""

    @abstractmethod
    async def save(self, *args, **kwargs):
        """Function for execute save operations."""
        raise NotImplementedError

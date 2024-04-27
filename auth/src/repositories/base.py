# stdlib
from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    async def read(self, *args, **kwargs):
        raise NotImplementedError


class MixinCreateRepository(BaseRepository):
    @abstractmethod
    async def create(self, *args, **kwargs):
        raise NotImplementedError


class MixinDeleteRepository(BaseRepository):
    @abstractmethod
    async def delete(self, *args, **kwargs):
        raise NotImplementedError


class MixinUpdateRepository(BaseRepository):
    @abstractmethod
    async def update(self, *args, **kwargs):
        raise NotImplementedError

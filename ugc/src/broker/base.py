from abc import ABC, abstractmethod


class BaseBrokerProducer(ABC):
    @abstractmethod
    async def produce(self, *args, **kwargs):
        raise NotImplementedError

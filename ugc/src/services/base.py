from abc import ABC, abstractmethod


class BaseDataService(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def send_message(self, *args, **kwargs):
        pass

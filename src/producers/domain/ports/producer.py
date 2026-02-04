from abc import ABC, abstractmethod
from typing import Any, Dict, Union


class BaseProducer(ABC):

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def status(self) -> str:
        pass

    @abstractmethod
    async def send(
        self, topic: str, key: str, value: Union[Dict[str, Any], bytes]
    ) -> None:
        pass

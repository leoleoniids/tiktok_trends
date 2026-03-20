from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from loguru import logger

T = TypeVar("T")

class BaseService(ABC, Generic[T]):
    """Abstract base for external services."""
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    @abstractmethod
    async def fetch(self, *args, **kwargs) -> List[T]:
        """Fetch data from the external source."""
        pass

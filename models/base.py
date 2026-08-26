from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseModelProvider(ABC):
    """Abstract base class establishing the interface for structured LLM inference."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Type[T]
    ) -> T:
        """Generates structured data matching the provided Pydantic response_schema."""
        pass

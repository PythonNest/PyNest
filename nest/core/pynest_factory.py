from abc import ABC, abstractmethod
from typing import Type, TypeVar

ModuleType = TypeVar("ModuleType")


class AbstractPyNestFactory(ABC):
    @abstractmethod
    def create(self, main_module: Type[ModuleType], **kwargs):
        raise NotImplementedError

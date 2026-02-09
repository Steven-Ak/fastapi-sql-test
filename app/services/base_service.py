from typing import Type, TypeVar, Generic
from app.core.exceptions import NotFoundException

T = TypeVar("T")

class BaseService(Generic[T]):
    def __init__(self, repo, model: Type[T]):
        self.repo = repo
        self.model = model

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, entity_id: int) -> T:
        entity = self.repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundException(self.model.__name__)
        return entity

    def delete(self, entity_id: int) -> bool:
        entity = self.get_by_id(entity_id)
        self.repo.delete(entity)
        return True
from typing import Generic, Optional, TypeVar, List
from sqlmodel import SQLModel, Session, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):

    def __init__(self, db: Session, model_class: type[T]):
        self.db = db
        self.model_class = model_class

    def get_all(self) -> List[T]:
        return self.db.exec(
            select(self.model_class)
        ).all()

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.get(self.model_class, id)

    def add(self, entity: T) -> T:
        self.db.add(entity)
        return entity

    # Alias para no romper el codigo que usa .create()
    def create(self, entity: T) -> T:
        return self.add(entity)

    def update(self, entity: T) -> T:
        self.db.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)

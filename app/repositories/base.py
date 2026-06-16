from typing import Generic, Optional, TypeVar, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):

    def __init__(self, db: Session, model_class: type[T]):
        self.db = db
        self.model_class = model_class

    def get_all(self) -> List[T]:
        stmt = select(self.model_class)
        if hasattr(self.model_class, 'deleted_at'):
            stmt = stmt.where(self.model_class.deleted_at.is_(None))
        return self.db.exec(stmt).all()

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
        if hasattr(entity, 'deleted_at'):
            entity.deleted_at = datetime.now(timezone.utc)
            self.db.add(entity)
        else:
            self.db.delete(entity)

from typing import Optional
from sqlmodel import Session, select
from app.models.categoria_model import Categoria
from app.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):

    def __init__(self, db: Session):
        super().__init__(db, Categoria)

    def get_all(self, parent_id: Optional[int] = None):
        statement = select(Categoria).where(Categoria.activo == True)

        if parent_id is not None:
            statement = statement.where(Categoria.parent_id == parent_id)

        return self.db.exec(statement).all()

    def get_by_id(self, categoria_id: int):
        return self.db.exec(
            select(Categoria).where(
                Categoria.id == categoria_id,
                Categoria.activo == True
            )
        ).first()

    def delete(self, categoria: Categoria):
        categoria.activo = False
        self.db.add(categoria)

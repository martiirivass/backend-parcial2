from datetime import datetime

from sqlmodel import Session, select, func

from app.models.ingrediente_model import Ingrediente
from app.repositories.base import BaseRepository


class IngredienteRepository(
    BaseRepository[Ingrediente]
):

    def __init__(self, db: Session):
        super().__init__(db, Ingrediente)

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ):

        statement = (
            select(Ingrediente)
            .where(
                Ingrediente.deleted_at.is_(None)
            )
            .offset(offset)
            .limit(limit)
        )

        return self.db.exec(statement).all()

    def count(self):

        statement = (
            select(func.count())
            .select_from(Ingrediente)
            .where(
                Ingrediente.deleted_at.is_(None)
            )
        )

        return self.db.exec(statement).one()

    def get_by_id(
        self,
        ingrediente_id: int
    ):

        statement = (
            select(Ingrediente)
            .where(
                Ingrediente.id == ingrediente_id,
                Ingrediente.deleted_at.is_(None)
            )
        )

        return self.db.exec(statement).first()

    def delete(
        self,
        ingrediente: Ingrediente
    ):

        ingrediente.deleted_at = datetime.now()

        self.db.add(ingrediente)

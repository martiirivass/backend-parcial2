from datetime import datetime
from sqlmodel import Session, select
from app.models.ingrediente_model import Ingrediente
from app.repositories.base import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):

    def __init__(self, db: Session):
        super().__init__(db, Ingrediente)

    def get_all(self):
        return self.db.exec(
            select(Ingrediente).where(Ingrediente.deleted_at == None)
        ).all()

    def get_by_id(self, ingrediente_id: int):
        return self.db.exec(
            select(Ingrediente).where(
                Ingrediente.id == ingrediente_id,
                Ingrediente.deleted_at == None
            )
        ).first()

    def delete(self, ingrediente: Ingrediente):
        ingrediente.deleted_at = datetime.now()
        self.db.add(ingrediente)

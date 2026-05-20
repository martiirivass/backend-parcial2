from sqlmodel import Session, select
from app.models.ingrediente_model import Ingrediente
from app.repositories.base import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):

    def __init__(self, db: Session):
        super().__init__(db, Ingrediente)

    def get_all(self):
        return self.db.exec(
            select(Ingrediente).where(Ingrediente.activo == True)
        ).all()

    def get_by_id(self, ingrediente_id: int):
        return self.db.exec(
            select(Ingrediente).where(
                Ingrediente.id == ingrediente_id,
                Ingrediente.activo == True
            )
        ).first()

    def delete(self, ingrediente: Ingrediente):
        ingrediente.activo = False
        self.db.add(ingrediente)

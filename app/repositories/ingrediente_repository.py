from sqlmodel import Session, select
from app.models.ingredient_model import Ingrediente


class IngredienteRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        statement = select(Ingrediente).where(Ingrediente.activo == True)
        return self.db.exec(statement).all()

    def get_by_id(self, ingrediente_id: int):
        statement = select(Ingrediente).where(
            Ingrediente.id == ingrediente_id,
            Ingrediente.activo == True
        )
        return self.db.exec(statement).first()

    def create(self, ingrediente: Ingrediente):
        self.db.add(ingrediente)
        return ingrediente

    def update(self, ingrediente: Ingrediente):
        self.db.add(ingrediente)
        return ingrediente

    def delete(self, ingrediente: Ingrediente):
        ingrediente.activo = False
        self.db.add(ingrediente)

from sqlmodel import Session, select
from app.models.categoria_model import Categoria


class CategoriaRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        statement = select(Categoria).where(Categoria.activo == True)
        return self.db.exec(statement).all()

    def get_by_id(self, categoria_id: int):
        statement = select(Categoria).where(
            Categoria.id == categoria_id,
            Categoria.activo == True
        )
        return self.db.exec(statement).first()

    def create(self, categoria: Categoria):
        self.db.add(categoria)
        return categoria

    def update(self, categoria: Categoria):
        self.db.add(categoria)
        return categoria

    def delete(self, categoria: Categoria):
        categoria.activo = False
        self.db.add(categoria)

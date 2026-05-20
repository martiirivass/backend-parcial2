from sqlmodel import Session, select
from app.models.producto_model import Producto


class ProductoRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        statement = select(Producto).where(Producto.activo == True)
        return self.db.exec(statement).all()

    def get_by_id(self, producto_id: int):
        statement = select(Producto).where(
            Producto.id == producto_id,
            Producto.activo == True
        )
        return self.db.exec(statement).first()

    def create(self, producto: Producto):
        self.db.add(producto)
        return producto

    def update(self, producto: Producto):
        self.db.add(producto)
        return producto

    def delete(self, producto: Producto):
        producto.activo = False
        self.db.add(producto)
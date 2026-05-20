from sqlmodel import Session, select
from app.models.producto_model import Producto
from app.repositories.base import BaseRepository


class ProductoRepository(BaseRepository[Producto]):

    def __init__(self, db: Session):
        super().__init__(db, Producto)

    def get_all(self):
        return self.db.exec(
            select(Producto).where(Producto.activo == True)
        ).all()

    def get_by_id(self, producto_id: int):
        return self.db.exec(
            select(Producto).where(
                Producto.id == producto_id,
                Producto.activo == True
            )
        ).first()

    def delete(self, producto: Producto):
        producto.activo = False
        self.db.add(producto)

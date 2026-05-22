from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Session, select, or_
from app.models.producto_model import Producto
from app.models.producto_categoria_model import ProductoCategoria
from app.repositories.base import BaseRepository


class ProductoRepository(BaseRepository[Producto]):

    def __init__(self, db: Session):
        super().__init__(db, Producto)

    def get_all(self):
        return self.db.exec(
            select(Producto).where(Producto.deleted_at == None)
        ).all()

    def get_by_id(self, producto_id: int):
        return self.db.exec(
            select(Producto).where(
                Producto.id == producto_id,
                Producto.deleted_at == None
            )
        ).first()

    def get_all_filtered(
        self,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        q: Optional[str] = None
    ):
        statement = select(Producto).where(Producto.deleted_at == None)

        # Filtro por categoria (join con tabla intermedia)
        if categoria_id is not None:
            statement = statement.join(
                ProductoCategoria,
                Producto.id == ProductoCategoria.producto_id
            ).where(
                ProductoCategoria.categoria_id == categoria_id
            )

        # Filtro por disponibilidad
        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)

        # Busqueda por texto
        if q is not None and q.strip():
            statement = statement.where(
                or_(
                    Producto.nombre.ilike(f"%{q}%"),
                    Producto.descripcion.ilike(f"%{q}%")
                )
            )

        return self.db.exec(statement).all()

    def delete(self, producto: Producto):
        producto.deleted_at = datetime.now(timezone.utc)
        self.db.add(producto)

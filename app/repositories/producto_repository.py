from typing import Optional
from datetime import datetime, timezone

from sqlmodel import (
    Session,
    select,
    or_,
    func
)

from app.models.producto_model import (
    Producto
)

from app.models.producto_categoria_model import (
    ProductoCategoria
)

from app.repositories.base import (
    BaseRepository
)


class ProductoRepository(
    BaseRepository[Producto]
):

    def __init__(self, db: Session):
        super().__init__(db, Producto)

    def get_by_id(
        self,
        producto_id: int
    ):

        statement = (
            select(Producto)
            .where(
                Producto.id == producto_id,
                Producto.deleted_at.is_(None)
            )
        )

        return self.db.exec(statement).first()

    def get_all_filtered(
        self,
        limit: int,
        offset: int,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        q: Optional[str] = None
    ):

        statement = (
            select(Producto)
            .where(
                Producto.deleted_at.is_(None)
            )
        )

        # Categoría
        if categoria_id is not None:

            statement = (
                statement
                .join(
                    ProductoCategoria,
                    Producto.id == ProductoCategoria.producto_id
                )
                .where(
                    ProductoCategoria.categoria_id
                    == categoria_id
                )
            )

        # Disponibilidad
        if disponible is not None:

            statement = statement.where(
                Producto.disponible == disponible
            )

        # Búsqueda
        if q and q.strip():

            statement = statement.where(
                or_(
                    Producto.nombre.ilike(f"%{q}%"),
                    Producto.descripcion.ilike(f"%{q}%")
                )
            )

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        return self.db.exec(statement).all()

    def count_filtered(
        self,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        q: Optional[str] = None
    ):

        statement = (
            select(func.count())
            .select_from(Producto)
            .where(
                Producto.deleted_at.is_(None)
            )
        )

        if categoria_id is not None:

            statement = (
                statement
                .join(
                    ProductoCategoria,
                    Producto.id == ProductoCategoria.producto_id
                )
                .where(
                    ProductoCategoria.categoria_id
                    == categoria_id
                )
            )

        if disponible is not None:

            statement = statement.where(
                Producto.disponible == disponible
            )

        if q and q.strip():

            statement = statement.where(
                or_(
                    Producto.nombre.ilike(f"%{q}%"),
                    Producto.descripcion.ilike(f"%{q}%")
                )
            )

        return self.db.exec(statement).one()

    def delete(
        self,
        producto: Producto
    ):

        producto.deleted_at = datetime.now(
            timezone.utc
        )

        self.db.add(producto)

from fastapi import HTTPException
from sqlmodel import select

from app.models.unidad_medida_model import (
    UnidadMedida
)
from app.models.producto_model import Producto
from app.models.producto_ingrediente_model import ProductoIngrediente

from app.repositories.unidad_medida_repository import (
    UnidadMedidaRepository
)


class UnidadMedidaService:

    def __init__(self, db):

        self.db = db
        self.repo = UnidadMedidaRepository(
            db
        )

    # Listar
    def listar(self):

        return self.repo.get_all()

    # Obtener
    def obtener(
        self,
        unidad_id: int
    ):

        unidad = self.repo.get_by_id(
            unidad_id
        )

        if not unidad:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Unidad de medida "
                    "no encontrada"
                )
            )

        return unidad

    # Crear
    def crear(
        self,
        datos
    ):

        unidad = UnidadMedida(
            **datos.model_dump()
        )

        self.repo.create(unidad)

        return unidad

    # Actualizar
    def actualizar(
        self,
        unidad_id: int,
        datos
    ):

        unidad = self.obtener(
            unidad_id
        )

        update_data = datos.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                unidad,
                key,
                value
            )

        self.repo.update(unidad)

        return unidad

    # Eliminar
    def eliminar(
        self,
        unidad_id: int
    ):

        unidad = self.obtener(
            unidad_id
        )

        # Check for associated products via unidad_venta_id
        producto = self.db.exec(
            select(Producto).where(
                Producto.unidad_venta_id == unidad_id,
                Producto.deleted_at == None
            )
        ).first()

        if producto:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"No se puede eliminar la unidad de medida "
                    f"porque está siendo usada como unidad de venta "
                    f"del producto \"{producto.nombre}\""
                )
            )

        # Check for associated product ingredients
        pi = self.db.exec(
            select(ProductoIngrediente).where(
                ProductoIngrediente.unidad_medida_id == unidad_id
            )
        ).first()

        if pi:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se puede eliminar la unidad de medida "
                    "porque está siendo usada en ingredientes "
                    "de productos"
                )
            )

        self.repo.delete(unidad)
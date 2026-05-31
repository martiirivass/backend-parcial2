from fastapi import HTTPException

from app.models.unidad_medida_model import (
    UnidadMedida
)

from app.repositories.unidad_medida_repository import (
    UnidadMedidaRepository
)


class UnidadMedidaService:

    def __init__(self, db):

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

        self.repo.delete(unidad)
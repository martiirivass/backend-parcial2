import logging

from fastapi import HTTPException

from app.models.ingrediente_model import Ingrediente

from app.repositories.ingrediente_repository import (
    IngredienteRepository
)

from app.schemas.common import paginated_response

logger = logging.getLogger(__name__)


class IngredienteService:

    def __init__(self, db):

        self.repo = IngredienteRepository(db)

    # Crear ingrediente
    def crear_ingrediente(
        self,
        ingrediente_data
    ):

        nuevo = Ingrediente(
            **ingrediente_data.model_dump()
        )

        self.repo.create(
            nuevo
        )

        return nuevo

    # Listar ingredientes
    def listar_ingredientes(
        self,
        limit: int,
        offset: int,
        q: str | None = None
    ):

        ingredientes = self.repo.get_all(
            limit=limit,
            offset=offset
        )

        if q:

            ingredientes = [
                ingrediente
                for ingrediente in ingredientes
                if q.lower() in ingrediente.nombre.lower()
            ]

        return paginated_response(
            ingredientes,
            len(ingredientes),
            page=(offset // limit) + 1,
            size=limit,
        )

    # Obtener ingrediente
    def obtener_ingrediente(
        self,
        ingrediente_id: int
    ):

        ingrediente = self.repo.get_by_id(
            ingrediente_id
        )

        if not ingrediente:

            raise HTTPException(
                status_code=404,
                detail="Ingrediente no encontrado"
            )

        return ingrediente

    # Actualizar ingrediente
    def actualizar_ingrediente(
        self,
        ingrediente_id: int,
        datos
    ):

        ingrediente = self.repo.get_by_id(
            ingrediente_id
        )

        if not ingrediente:

            raise HTTPException(
                status_code=404,
                detail="Ingrediente no encontrado"
            )

        update_data = datos.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                ingrediente,
                key,
                value
            )

        self.repo.update(
            ingrediente
        )

        return ingrediente

    # Eliminar ingrediente
    def eliminar_ingrediente(
        self,
        ingrediente_id: int
    ):

        ingrediente = self.repo.get_by_id(
            ingrediente_id
        )

        if not ingrediente:

            raise HTTPException(
                status_code=404,
                detail="Ingrediente no encontrado"
            )

        self.repo.delete(
            ingrediente
        )
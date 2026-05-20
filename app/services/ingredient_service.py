import logging

from fastapi import HTTPException

from app.models.ingredient_model import Ingrediente
from app.repositories.ingredient_repository import IngredienteRepository
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class IngredienteService:

    def __init__(self, db):
        self.db = db
        self.repo = IngredienteRepository(db)
        self.uow = UnitOfWork(db)

    # Crear ingrediente
    def crear_ingrediente(self, ingrediente_data):

        try:

            nuevo = Ingrediente(
                **ingrediente_data.model_dump()
            )

            self.repo.create(nuevo)

            self.uow.commit()
            self.db.refresh(nuevo)

            return nuevo

        except Exception as e:
            logger.exception(f"Error creating ingrediente: {e}")
            self.uow.rollback()
            raise

    # Listar ingredientes
    def listar_ingredientes(self, limit: int, offset: int):

        ingredientes = self.repo.get_all()

        return {
            "data": ingredientes[offset: offset + limit],
            "total": len(ingredientes)
        }

    # Obtener ingrediente
    def obtener_ingrediente(self, ingrediente_id: int):

        ingrediente = self.repo.get_by_id(ingrediente_id)

        if not ingrediente:
            raise HTTPException(
                status_code=404,
                detail="Ingrediente no encontrado"
            )

        return ingrediente

    # Actualizar ingrediente
    def actualizar_ingrediente(self, ingrediente_id: int, datos):

        try:

            ingrediente = self.repo.get_by_id(ingrediente_id)

            if not ingrediente:
                raise HTTPException(
                    status_code=404,
                    detail="Ingrediente no encontrado"
                )

            update_data = datos.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(ingrediente, key, value)

            self.repo.update(ingrediente)

            self.uow.commit()
            self.db.refresh(ingrediente)

            return ingrediente

        except Exception as e:
            logger.exception(f"Error updating ingrediente: {e}")
            self.uow.rollback()
            raise

    # Eliminar ingrediente
    def eliminar_ingrediente(self, ingrediente_id: int):

        try:

            ingrediente = self.repo.get_by_id(ingrediente_id)

            if not ingrediente:
                raise HTTPException(
                    status_code=404,
                    detail="Ingrediente no encontrado"
                )

            self.repo.delete(ingrediente)

            self.uow.commit()

        except Exception as e:
            logger.exception(f"Error deleting ingrediente: {e}")
            self.uow.rollback()
            raise
import logging

from fastapi import HTTPException

from app.repositories.forma_pago_repository import (
    FormaPagoRepository
)

logger = logging.getLogger(__name__)


class FormaPagoService:

    def __init__(self, db):

        self.repo = FormaPagoRepository(
            db
        )

    def listar(self):
        """Lista todas las formas de pago."""
        return self.repo.get_all()

    def obtener(
        self,
        codigo: str
    ):
        """Obtiene una forma de pago por su código."""
        fp = self.repo.get_by_codigo(
            codigo
        )

        if not fp:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Forma de pago "
                    "no encontrada"
                )
            )

        return fp

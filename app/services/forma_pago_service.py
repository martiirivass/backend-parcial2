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

    # Listar formas de pago
    def listar(self):

        return self.repo.get_all()

    # Obtener forma de pago por codigo
    def obtener(
        self,
        codigo: str
    ):

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

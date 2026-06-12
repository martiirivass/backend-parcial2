import logging

from fastapi import HTTPException

from app.models.pago_model import Pago

from app.repositories.pago_repository import (
    PagoRepository
)

logger = logging.getLogger(__name__)


class PagoService:

    def __init__(self, db):

        self.repo = PagoRepository(db)

    def registrar_pago(self, datos):

        pedido = self.repo.get_pedido_by_id(
            datos.pedido_id
        )

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail="Pedido no encontrado"
            )

        pago = Pago(
            pedido_id=datos.pedido_id,
            external_reference=str(datos.pedido_id),
        )

        self.repo.create(pago)

        return pago

    def listar_por_pedido(
        self,
        pedido_id: int
    ):

        return self.repo.get_by_pedido(
            pedido_id
        )

    def listar_todos(self):

        return self.repo.get_all()

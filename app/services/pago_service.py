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

        pagos_actuales = self.repo.get_by_pedido(
            datos.pedido_id
        )

        total_pagado = sum(
            pago.monto
            for pago in pagos_actuales
        )

        saldo_pendiente = (
            pedido.total - total_pagado
        )

        if datos.monto > saldo_pendiente:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"El pago excede el saldo pendiente "
                    f"({saldo_pendiente:.2f})"
                )
            )

        pago = Pago(
            pedido_id=datos.pedido_id,
            monto=datos.monto,
            forma_pago_codigo=datos.forma_pago_codigo,
            referencia=datos.referencia
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

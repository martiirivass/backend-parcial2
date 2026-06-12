import logging

from fastapi import HTTPException

from app.repositories.estado_pedido_repository import (
    EstadoPedidoRepository
)

logger = logging.getLogger(__name__)


class EstadoPedidoService:

    def __init__(self, db):

        self.repo = EstadoPedidoRepository(
            db
        )

    # Listar estados de pedido
    def listar(self):

        return self.repo.get_all()

    # Obtener estado de pedido por codigo
    def obtener(
        self,
        codigo: str
    ):

        ep = self.repo.get_by_codigo(
            codigo
        )

        if not ep:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Estado de pedido "
                    "no encontrado"
                )
            )

        return ep

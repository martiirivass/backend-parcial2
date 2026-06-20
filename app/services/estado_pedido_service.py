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

    def listar(self):
        """Lista todos los estados de pedido."""
        return self.repo.get_all()

    def obtener(
        self,
        codigo: str
    ):
        """Obtiene un estado de pedido por su código."""
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

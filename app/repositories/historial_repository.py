from sqlmodel import Session, select

from app.models.historial_estado_model import (
    HistorialEstadoPedido
)

from app.repositories.base import BaseRepository


class HistorialRepository(
    BaseRepository[HistorialEstadoPedido]
):

    def __init__(self, db: Session):
        super().__init__(
            db,
            HistorialEstadoPedido
        )

    def get_by_pedido_id(
        self,
        pedido_id: int
    ):

        return self.db.exec(
            select(HistorialEstadoPedido)
            .where(
                HistorialEstadoPedido.pedido_id == pedido_id
            )
            .order_by(
                HistorialEstadoPedido.created_at
            )
        ).all()
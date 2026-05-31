from sqlmodel import Session, select

from app.models.estado_pedido_model import EstadoPedido
from app.repositories.base import BaseRepository


class EstadoPedidoRepository(
    BaseRepository[EstadoPedido]
):

    def __init__(self, db: Session):
        super().__init__(db, EstadoPedido)

    def get_by_codigo(
        self,
        codigo: str
    ):

        return self.db.exec(
            select(EstadoPedido).where(
                EstadoPedido.codigo == codigo
            )
        ).first()
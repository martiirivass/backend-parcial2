from sqlmodel import Session, select

from app.models.pago_model import Pago
from app.models.pedido_model import Pedido

from app.repositories.base import BaseRepository


class PagoRepository(
    BaseRepository[Pago]
):

    def __init__(self, db: Session):
        super().__init__(db, Pago)

    def get_by_pedido(
        self,
        pedido_id: int
    ):

        statement = (
            select(Pago)
            .where(
                Pago.pedido_id == pedido_id
            )
        )

        return self.db.exec(statement).all()

    def get_pedido_by_id(
        self,
        pedido_id: int
    ):

        return self.db.get(
            Pedido,
            pedido_id
        )
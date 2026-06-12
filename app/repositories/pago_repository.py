from sqlmodel import Session, select
<<<<<<< HEAD
from app.models.pago_model import Pago
from app.repositories.base import BaseRepository


class PagoRepository(BaseRepository[Pago]):
=======

from app.models.pago_model import Pago
from app.models.pedido_model import Pedido

from app.repositories.base import BaseRepository


class PagoRepository(
    BaseRepository[Pago]
):
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

    def __init__(self, db: Session):
        super().__init__(db, Pago)

<<<<<<< HEAD
    def get_by_pedido(self, pedido_id: int):
        return self.db.exec(
            select(Pago).where(Pago.pedido_id == pedido_id)
        ).all()
=======
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
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

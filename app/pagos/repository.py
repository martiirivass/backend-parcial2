from typing import Optional

from sqlmodel import Session, select

from app.models.pago_model import Pago
from app.repositories.base import BaseRepository


class PagoRepository(BaseRepository[Pago]):

    def __init__(self, db: Session):
        super().__init__(db, Pago)

    def get_by_pedido_id(self, pedido_id: int) -> list[Pago]:
        statement = select(Pago).where(
            Pago.pedido_id == pedido_id
        )
        return self.db.exec(statement).all()

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Optional[Pago]:
        statement = select(Pago).where(
            Pago.mp_payment_id == mp_payment_id
        )
        return self.db.exec(statement).first()

    def get_by_external_reference(self, external_reference: str) -> Optional[Pago]:
        statement = select(Pago).where(
            Pago.external_reference == external_reference
        )
        return self.db.exec(statement).first()

from sqlmodel import Session, select

from app.models.forma_pago_model import FormaPago
from app.repositories.base import BaseRepository


class FormaPagoRepository(
    BaseRepository[FormaPago]
):

    def __init__(self, db: Session):
        super().__init__(db, FormaPago)

    def get_by_codigo(
        self,
        codigo: str
    ):

        return self.db.exec(
            select(FormaPago).where(
                FormaPago.codigo == codigo
            )
        ).first()

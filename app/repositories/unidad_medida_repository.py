from sqlmodel import Session, select

from app.models.unidad_medida_model import UnidadMedida

from app.repositories.base import BaseRepository


class UnidadMedidaRepository(
    BaseRepository[UnidadMedida]
):

    def __init__(self, db: Session):
        super().__init__(db, UnidadMedida)

    def get_all(self):

        statement = select(
            UnidadMedida
        )

        return self.db.exec(statement).all()

    def get_by_id(
        self,
        unidad_id: int
    ):

        statement = (
            select(UnidadMedida)
            .where(
                UnidadMedida.id == unidad_id
            )
        )

        return self.db.exec(statement).first()

    def delete(
        self,
        unidad: UnidadMedida
    ):

        self.db.delete(unidad)
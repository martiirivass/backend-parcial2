from datetime import datetime, timezone
<<<<<<< HEAD
from sqlmodel import Session, select
=======

from sqlmodel import Session, select

>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
from app.models.direccion_entrega_model import DireccionEntrega
from app.repositories.base import BaseRepository


<<<<<<< HEAD
class DireccionEntregaRepository(BaseRepository[DireccionEntrega]):
=======
class DireccionEntregaRepository(
    BaseRepository[DireccionEntrega]
):
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

    def __init__(self, db: Session):
        super().__init__(db, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int):
<<<<<<< HEAD
        return self.db.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at == None
            )
        ).all()

    def get_by_id(self, direccion_id: int):
        return self.db.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.id == direccion_id,
                DireccionEntrega.deleted_at == None
            )
        ).first()

    def delete(self, direccion: DireccionEntrega):
        direccion.deleted_at = datetime.now(timezone.utc)
        self.db.add(direccion)
=======

        statement = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None)
            )
        )

        return self.db.exec(statement).all()

    def get_by_id(self, direccion_id: int):

        statement = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.id == direccion_id,
                DireccionEntrega.deleted_at.is_(None)
            )
        )

        return self.db.exec(statement).first()

    def delete(self, direccion: DireccionEntrega):

        direccion.deleted_at = datetime.now(timezone.utc)

        self.db.add(direccion)
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

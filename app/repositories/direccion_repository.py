from sqlmodel import Session, select
from app.models.direccion_model import Direccion
from app.repositories.base import BaseRepository


class DireccionRepository(BaseRepository[Direccion]):

    def __init__(self, db: Session):
        super().__init__(db, Direccion)

    def get_by_usuario(self, usuario_id: int):
        return self.db.exec(
            select(Direccion).where(
                Direccion.usuario_id == usuario_id,
                Direccion.deleted_at == None
            )
        ).all()

    def get_by_id(self, direccion_id: int):
        return self.db.exec(
            select(Direccion).where(
                Direccion.id == direccion_id,
                Direccion.deleted_at == None
            )
        ).first()

    def delete(self, direccion: Direccion):
        from datetime import datetime, timezone
        direccion.deleted_at = datetime.now(timezone.utc)
        self.db.add(direccion)

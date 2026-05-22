from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.direccion_entrega_model import DireccionEntrega
from app.repositories.base import BaseRepository


class DireccionEntregaRepository(BaseRepository[DireccionEntrega]):

    def __init__(self, db: Session):
        super().__init__(db, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int):
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

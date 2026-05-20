from sqlmodel import Session, select
from app.models.pedido_model import Pedido
from app.repositories.base import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):

    def __init__(self, db: Session):
        super().__init__(db, Pedido)

    def get_all(self):
        return self.db.exec(
            select(Pedido).where(Pedido.activo == True)
        ).all()

    def get_by_id(self, pedido_id: int):
        return self.db.exec(
            select(Pedido).where(
                Pedido.id == pedido_id,
                Pedido.activo == True
            )
        ).first()

    def get_by_usuario(self, usuario_id: int):
        return self.db.exec(
            select(Pedido).where(
                Pedido.usuario_id == usuario_id,
                Pedido.activo == True
            )
        ).all()

    def delete(self, pedido: Pedido):
        pedido.activo = False
        self.db.add(pedido)

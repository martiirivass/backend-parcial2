from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, func, select
from app.models.pedido_model import Pedido
from app.repositories.base import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):

    def __init__(self, db: Session):
        super().__init__(db, Pedido)

    def get_all(self):
        return self.db.exec(
            select(Pedido).where(Pedido.deleted_at == None)
        ).all()

    def get_by_id(self, pedido_id: int):
        return self.db.exec(
            select(Pedido).where(
                Pedido.id == pedido_id,
                Pedido.deleted_at == None
            )
        ).first()

    def get_by_usuario(self, usuario_id: int):
        return self.db.exec(
            select(Pedido).where(
                Pedido.usuario_id == usuario_id,
                Pedido.deleted_at == None
            )
        ).all()

    def get_paginated(
        self,
        limit: int,
        offset: int,
        usuario_id: Optional[int] = None,
        estado_codigo: Optional[str] = None,
    ):
        statement = select(Pedido).where(
            Pedido.deleted_at == None
        )
        if usuario_id is not None:
            statement = statement.where(
                Pedido.usuario_id == usuario_id
            )
        if estado_codigo is not None:
            statement = statement.where(
                Pedido.estado_codigo == estado_codigo
            )
        return self.db.exec(
            statement.offset(offset).limit(limit)
        ).all()

    def count(
        self,
        usuario_id: Optional[int] = None,
        estado_codigo: Optional[str] = None,
    ):
        statement = select(func.count()).select_from(
            Pedido
        ).where(
            Pedido.deleted_at == None
        )
        if usuario_id is not None:
            statement = statement.where(
                Pedido.usuario_id == usuario_id
            )
        if estado_codigo is not None:
            statement = statement.where(
                Pedido.estado_codigo == estado_codigo
            )
        return self.db.exec(statement).one()

    def delete(self, pedido: Pedido):
        pedido.deleted_at = datetime.now(timezone.utc)
        self.db.add(pedido)

from typing import Optional

from sqlmodel import Field, SQLModel


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estados_pedido"

    codigo: str = Field(default=None, primary_key=True, max_length=20)
    descripcion: str = Field(max_length=80)
    orden: int
    es_terminal: bool

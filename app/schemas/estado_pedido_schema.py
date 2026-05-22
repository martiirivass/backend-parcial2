from typing import Optional
from sqlmodel import SQLModel


class EstadoPedidoRead(SQLModel):
    codigo: str
    descripcion: str
    orden: int
    es_terminal: bool

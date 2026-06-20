from typing import Optional
from sqlmodel import SQLModel


class EstadoPedidoRead(SQLModel):
    """Modelo de lectura para un estado de pedido (código, descripción, orden, es_terminal)."""
    codigo: str
    descripcion: str
    orden: int
    es_terminal: bool

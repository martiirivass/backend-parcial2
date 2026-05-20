from typing import Optional
from sqlmodel import SQLModel, Field


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str  # PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO
    nombre: str

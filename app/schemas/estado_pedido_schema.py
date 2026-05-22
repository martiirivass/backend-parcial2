from typing import Optional
from sqlmodel import SQLModel


class EstadoPedidoRead(SQLModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

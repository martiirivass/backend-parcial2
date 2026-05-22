from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class HistorialEstadoRead(SQLModel):
    id: int
    pedido_id: int
    estado_anterior: Optional[str] = None
    estado_nuevo: str
    usuario_id: int
    created_at: datetime

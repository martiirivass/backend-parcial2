from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class HistorialEstadoRead(SQLModel):
    id: int
    pedido_id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    created_at: datetime

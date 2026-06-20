from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class HistorialEstadoRead(SQLModel):
    """Modelo de lectura para una entrada del historial de estados de pedido."""
    id: int
    pedido_id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    created_at: datetime

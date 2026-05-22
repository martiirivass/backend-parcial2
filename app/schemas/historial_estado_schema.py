from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class HistorialEstadoRead(SQLModel):
    id: int
    pedido_id: int
    estado_codigo: str
    observacion: Optional[str] = None
    fecha: datetime

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class PagoCreate(SQLModel):
    pedido_id: int
    monto: float
    forma_pago_codigo: str
    referencia: Optional[str] = None


class PagoRead(SQLModel):
    id: int
    pedido_id: int
    monto: float
    forma_pago_codigo: str
    referencia: Optional[str] = None
    created_at: datetime

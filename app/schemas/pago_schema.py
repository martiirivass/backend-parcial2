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
    mp_payment_id: Optional[int] = None
    mp_status: Optional[str] = None
    external_reference: str
    idempotency_key: Optional[str] = None
    transaction_amount: Optional[float] = None
    date_approved: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

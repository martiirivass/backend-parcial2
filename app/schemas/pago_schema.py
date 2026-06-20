from decimal import Decimal
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class PagoCreate(SQLModel):
    """Esquema para crear un registro de pago."""
    pedido_id: int
    monto: Decimal
    forma_pago_codigo: str
    referencia: Optional[str] = None


class PagoRead(SQLModel):
    """Modelo de lectura para un pago con campos de integración de Mercado Pago."""
    id: int
    pedido_id: int
    mp_payment_id: Optional[int] = None
    mp_status: Optional[str] = None
    mp_status_detail: Optional[str] = None
    payment_method_id: Optional[str] = None
    external_reference: str
    idempotency_key: Optional[str] = None
    transaction_amount: Optional[Decimal] = None
    date_approved: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

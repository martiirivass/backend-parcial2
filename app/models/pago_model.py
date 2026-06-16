from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido


class Pago(SQLModel, table=True):
    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True)

    mp_payment_id: Optional[int] = Field(default=None, sa_type=BigInteger, index=True)
    mp_status: Optional[str] = Field(default=None, max_length=20)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)

    external_reference: str = Field(unique=True, max_length=100, index=True)
    idempotency_key: Optional[str] = Field(default=None, max_length=100)

    transaction_amount: Optional[float] = Field(default=None)
    payment_method_id: Optional[str] = Field(default=None, max_length=50)
    date_approved: Optional[datetime] = Field(default=None)

    creado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actualizado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="pagos")

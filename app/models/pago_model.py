from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido


class Pago(SQLModel, table=True):
    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")
    monto: float
    forma_pago_codigo: str = Field(foreign_key="formas_pago.codigo", max_length=20)
    referencia: Optional[str] = Field(
    default=None,
    max_length=100
)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="pagos")

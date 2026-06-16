from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, Column, Numeric

if TYPE_CHECKING:
    from app.models.detalle_pedido_model import DetallePedido
    from app.models.historial_estado_model import HistorialEstadoPedido
    from app.models.pago_model import Pago


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_pedido_subtotal"),
        CheckConstraint("descuento >= 0", name="ck_pedido_descuento"),
        CheckConstraint("costo_envio >= 0", name="ck_pedido_envio"),
        CheckConstraint("total >= 0", name="ck_pedido_total"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    direccion_id: Optional[int] = Field(
        default=None, foreign_key="direcciones_entrega.id"
    )
    estado_codigo: str = Field(
        default="PENDIENTE", foreign_key="estados_pedido.codigo", max_length=20
    )
    forma_pago_codigo: str = Field(
        foreign_key="formas_pago.codigo", max_length=20
    )

    # Snapshot monetario (inmutable desde creación) — DECIMAL(10,2)
    subtotal: Decimal = Field(default=Decimal('0.00'), sa_column=Column(Numeric(10, 2)))
    descuento: Decimal = Field(default=Decimal('0.00'), sa_column=Column(Numeric(10, 2)))
    costo_envio: Decimal = Field(default=Decimal('50.00'), sa_column=Column(Numeric(10, 2)))
    total: Decimal = Field(default=Decimal('0.00'), sa_column=Column(Numeric(10, 2)))

    notas: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    # Relaciones
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: List["HistorialEstadoPedido"] = Relationship(
        back_populates="pedido"
    )
    pagos: List["Pago"] = Relationship(back_populates="pedido")

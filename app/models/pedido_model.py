from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Numeric, CheckConstraint

if TYPE_CHECKING:
    from app.models.detalle_pedido_model import DetallePedido
    from app.models.historial_estado_model import HistorialEstadoPedido
    from app.models.pago_model import Pago


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

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

    # Snapshot monetario (inmutable desde creación)
    subtotal: Decimal = Field(default=Decimal('0'), sa_column=Column(Numeric(10, 2)))
    descuento: Decimal = Field(default=Decimal('0'), sa_column=Column(Numeric(10, 2)))
    costo_envio: Decimal = Field(default=Decimal('50'), sa_column=Column(Numeric(10, 2)))
    total: Decimal = Field(
        default=Decimal('0'),
        sa_column=Column(Numeric(10, 2), CheckConstraint("total >= 0"))
    )

    notas: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relaciones
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: List["HistorialEstadoPedido"] = Relationship(
        back_populates="pedido"
    )
    pagos: List["Pago"] = Relationship(back_populates="pedido")

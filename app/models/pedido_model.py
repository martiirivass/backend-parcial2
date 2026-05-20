from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.estado_pedido_model import EstadoPedido
    from app.models.forma_pago_model import FormaPago


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total: float = Field(default=0.0)
    estado_actual_id: int = Field(foreign_key="estados_pedido.id")
    forma_pago_id: int = Field(foreign_key="formas_pago.id")
    direccion_entrega_id: Optional[int] = Field(default=None, foreign_key="direcciones.id")
    activo: bool = Field(default=True)

    # Relaciones
    usuario: "Usuario" = Relationship(back_populates="pedidos")
    estado_actual: "EstadoPedido" = Relationship()
    forma_pago: "FormaPago" = Relationship()
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")

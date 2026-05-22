from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido
    from app.models.estado_pedido_model import EstadoPedido


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")
    estado_codigo: str = Field(foreign_key="estados_pedido.codigo", max_length=20)
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observacion: Optional[str] = None

    pedido: "Pedido" = Relationship(back_populates="historial_estados")
    estado: "EstadoPedido" = Relationship()

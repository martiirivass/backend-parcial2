from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")
    estado_anterior: Optional[str] = Field(default=None, foreign_key="estados_pedido.codigo", max_length=20)
    estado_nuevo: str = Field(foreign_key="estados_pedido.codigo", max_length=20)
    usuario_id: int = Field(foreign_key="usuarios.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="historial_estados")

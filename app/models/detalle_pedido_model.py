from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import ARRAY, Integer

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalles_pedido"

    pedido_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="pedidos.id"
    )
    producto_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="productos.id"
    )
    cantidad: int = Field(default=1)

    # Snapshot (inmutable desde creación)
    nombre_snapshot: str = Field(max_length=200)
    precio_snapshot: float = Field(default=0.0)
    subtotal_snap: float = Field(default=0.0)

    # IDs de ingredientes removidos (ej: [3, 7])
    personalizacion: Optional[str] = Field(
        default=None, sa_column=Column(ARRAY(Integer))
    )

    # Solo created_at — fila inmutable (sin updated_at)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="detalles")

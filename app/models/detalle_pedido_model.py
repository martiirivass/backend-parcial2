from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalles_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")

    # Snapshot Pattern: guardo el nombre y precio inmutables
    producto_id: int = Field(foreign_key="productos.id")
    nombre_producto: str  # Se guarda en el momento de crear el pedido
    precio_unitario: float  # Se guarda en el momento de crear el pedido
    cantidad: int = Field(default=1)
    subtotal: float = Field(default=0.0)

    pedido: "Pedido" = Relationship(back_populates="detalles")

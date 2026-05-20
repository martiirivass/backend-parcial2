from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import field_validator


class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: int = Field(default=1, ge=1)

    @field_validator("cantidad")
    def validar_cantidad(cls, v):
        if v < 1:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class PedidoCreate(SQLModel):
    forma_pago_id: int
    direccion_entrega_id: Optional[int] = None
    items: List[DetallePedidoCreate]

    @field_validator("items")
    def validar_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe incluir al menos un producto")
        return v


class AvanceEstadoRequest(SQLModel):
    estado_id: int


class DetallePedidoRead(SQLModel):
    id: int
    producto_id: int
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class HistorialEstadoRead(SQLModel):
    id: int
    estado_pedido_id: int
    fecha: datetime
    observacion: Optional[str] = None


class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    fecha: datetime
    total: float
    estado_actual_id: int
    forma_pago_id: int
    direccion_entrega_id: Optional[int] = None
    activo: bool


class PedidoReadWithDetalles(PedidoRead):
    detalles: List[DetallePedidoRead] = []
    historial_estados: List[HistorialEstadoRead] = []

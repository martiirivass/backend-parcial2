from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import field_validator

from app.schemas.historial_estado_schema import HistorialEstadoRead
from app.schemas.pago_schema import PagoRead


class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: int = Field(default=1, ge=1)

    @field_validator("cantidad")
    def validar_cantidad(cls, v):
        if v < 1:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class PedidoCreate(SQLModel):
    forma_pago_codigo: str
    direccion_id: Optional[int] = None
    items: List[DetallePedidoCreate]
    referencia_pago: Optional[str] = Field(
        default=None, max_length=200,
        description="Referencia del pago (CBU para transferencia, últimos 4 dígitos para tarjeta)"
    )

    @field_validator("items")
    def validar_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe incluir al menos un producto")
        return v


class AvanceEstadoRequest(SQLModel):
    estado_codigo: str


class CancelarPedidoRequest(SQLModel):
    motivo: str


class DetallePedidoRead(SQLModel):
    pedido_id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: float
    cantidad: int
    subtotal_snap: float
    personalizacion: Optional[str] = None
    created_at: datetime


class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    direccion_id: Optional[int] = None
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PedidoReadWithDetails(PedidoRead):
    detalles: List[DetallePedidoRead] = []
    historial_estados: List[HistorialEstadoRead] = []
    pagos: List[PagoRead] = []


class PedidoListResponse(SQLModel):
    data: List[PedidoReadWithDetails]
    total: int

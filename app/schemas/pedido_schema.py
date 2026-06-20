from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import field_validator

from app.schemas.historial_estado_schema import HistorialEstadoRead
from app.schemas.pago_schema import PagoRead


class DetallePedidoCreate(SQLModel):
    """Esquema para un ítem individual en un pedido nuevo."""
    producto_id: int
    cantidad: int = Field(default=1, ge=1)
    personalizacion: Optional[list[int]] = None

    @field_validator("cantidad")
    def validar_cantidad(cls, v):
        if v < 1:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class PedidoCreate(SQLModel):
    """Esquema para crear un nuevo pedido con ítems e información de pago."""
    forma_pago_codigo: str
    direccion_id: Optional[int] = None
    notas: Optional[str] = None
    items: List[DetallePedidoCreate]
    referencia_pago: Optional[str] = Field(
        default=None, max_length=200,
        description="Referencia del pago (CBU para transferencia, últimos 4 dígitos para tarjeta)"
    )
    codigo_descuento: Optional[str] = Field(
        default=None, max_length=20,
        description="Código de descuento promocional"
    )

    @field_validator("items")
    def validar_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe incluir al menos un producto")
        return v


class AvanceEstadoRequest(SQLModel):
    """Cuerpo de la solicitud para avanzar un pedido al siguiente estado."""
    estado_codigo: str
    motivo: Optional[str] = None


class CancelarPedidoRequest(SQLModel):
    """Cuerpo de la solicitud para cancelar un pedido."""
    motivo: Optional[str] = None


class DetallePedidoRead(SQLModel):
    """Modelo de lectura para un detalle de pedido con valores snapshot."""
    pedido_id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    cantidad: int
    subtotal_snap: Decimal
    personalizacion: Optional[str] = None
    created_at: datetime


class PedidoRead(SQLModel):
    """Modelo de lectura para un pedido con totales y marcas de tiempo."""
    id: int
    usuario_id: int
    direccion_id: Optional[int] = None
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: Decimal
    descuento: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PedidoReadWithDetails(PedidoRead):
    """Pedido con detalles, historial de estados y pagos incluidos."""
    detalles: List[DetallePedidoRead] = []
    historial_estados: List[HistorialEstadoRead] = []
    pagos: List[PagoRead] = []


class PedidoListResponse(SQLModel):
    """Respuesta paginada para la lista de pedidos."""
    data: List[PedidoReadWithDetails]
    total: int
    page: int
    size: int
    pages: int

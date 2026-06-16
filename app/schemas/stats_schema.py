from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel


class ResumenStats(SQLModel):
    ventas_totales: Decimal = Decimal('0.00')
    pedidos_hoy: int = 0
    clientes_nuevos: int = 0
    pedidos_pendientes: int = 0


class VentaDiaria(SQLModel):
    fecha: date
    total: Decimal = Decimal('0.00')
    cantidad: int = 0


class VentasSemanalesResponse(SQLModel):
    data: list[VentaDiaria]


class ProductoMasVendido(SQLModel):
    producto_id: int
    nombre: str
    total_vendido: int = 0
    ingreso_total: Decimal = Decimal('0.00')


class ProductosMasVendidosResponse(SQLModel):
    data: list[ProductoMasVendido]


class PedidosPorEstadoItem(SQLModel):
    estado_codigo: str
    cantidad: int = 0


class PedidosPorEstadoResponse(SQLModel):
    data: list[PedidosPorEstadoItem]


class IngresoPorFormaPagoItem(SQLModel):
    forma_pago_codigo: str
    total: Decimal = Decimal('0.00')
    cantidad: int = 0


class IngresosPorFormaPagoResponse(SQLModel):
    data: list[IngresoPorFormaPagoItem]

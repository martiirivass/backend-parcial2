from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel


class ResumenStats(SQLModel):
    """Respuesta del endpoint de resumen del dashboard."""
    ventas_totales: Decimal = Decimal('0')
    pedidos_hoy: int = 0
    clientes_nuevos: int = 0
    pedidos_pendientes: int = 0


class VentaDiaria(SQLModel):
    """Ventas agregadas de un día específico."""
    fecha: date
    total: Decimal = Decimal('0')
    cantidad: int = 0


class VentasSemanalesResponse(SQLModel):
    """Respuesta del endpoint de ventas semanales."""
    data: list[VentaDiaria]


class ProductoMasVendido(SQLModel):
    """Producto con su cantidad vendida e ingreso total."""
    producto_id: int
    nombre: str
    total_vendido: int = 0
    ingreso_total: Decimal = Decimal('0')


class ProductosMasVendidosResponse(SQLModel):
    """Respuesta del endpoint de productos más vendidos."""
    data: list[ProductoMasVendido]

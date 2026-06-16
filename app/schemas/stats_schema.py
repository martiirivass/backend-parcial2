from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel


class ResumenStats(SQLModel):
    """Respuesta del endpoint de resumen del dashboard."""
    ventas_totales: float = 0.0
    pedidos_hoy: int = 0
    clientes_nuevos: int = 0
    pedidos_pendientes: int = 0


class VentaDiaria(SQLModel):
    """Ventas agregadas de un día específico."""
    fecha: date
    total: float = 0.0
    cantidad: int = 0


class VentasSemanalesResponse(SQLModel):
    """Respuesta del endpoint de ventas semanales."""
    data: list[VentaDiaria]


class ProductoMasVendido(SQLModel):
    """Producto con su cantidad vendida e ingreso total."""
    producto_id: int
    nombre: str
    total_vendido: int = 0
    ingreso_total: float = 0.0


class ProductosMasVendidosResponse(SQLModel):
    """Respuesta del endpoint de productos más vendidos."""
    data: list[ProductoMasVendido]


class PedidosPorEstadoItem(SQLModel):
    """Cantidad de pedidos agrupados por estado."""
    estado_codigo: str
    cantidad: int = 0


class PedidosPorEstadoResponse(SQLModel):
    """Respuesta del endpoint de pedidos por estado."""
    data: list[PedidosPorEstadoItem]


class IngresoPorFormaPagoItem(SQLModel):
    """Ingresos agrupados por forma de pago."""
    forma_pago_codigo: str
    total: float = 0.0
    cantidad: int = 0


class IngresosPorFormaPagoResponse(SQLModel):
    """Respuesta del endpoint de ingresos por forma de pago."""
    data: list[IngresoPorFormaPagoItem]

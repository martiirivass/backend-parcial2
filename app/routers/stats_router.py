from fastapi import APIRouter, Depends, Query
from typing import Annotated
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.stats_schema import (
    ResumenStats,
    VentasSemanalesResponse,
    ProductosMasVendidosResponse,
    PedidosPorEstadoResponse,
    IngresosPorFormaPagoResponse,
)
from app.services.stats_service import StatsService
from app.auth.permissions import require_roles

router = APIRouter(
    prefix="/admin/stats",
    tags=["Admin Stats"]
)


# Resumen de estadísticas del dashboard
@router.get("/resumen", response_model=ResumenStats)
def obtener_resumen(
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_resumen()


# Ventas semanales para gráfico
@router.get("/ventas-semanales", response_model=VentasSemanalesResponse)
def obtener_ventas_semanales(
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_ventas_semanales()


# Productos más vendidos
@router.get("/productos-mas-vendidos", response_model=ProductosMasVendidosResponse)
def obtener_productos_mas_vendidos(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_productos_mas_vendidos(limit=limit)


# Pedidos agrupados por estado (para gráfico PieChart)
@router.get("/pedidos-por-estado", response_model=PedidosPorEstadoResponse)
def obtener_pedidos_por_estado(
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_pedidos_por_estado()


# Ingresos agrupados por forma de pago (para gráfico BarChart)
@router.get("/ingresos-por-forma-pago", response_model=IngresosPorFormaPagoResponse)
def obtener_ingresos_por_forma_pago(
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_ingresos_por_forma_pago()

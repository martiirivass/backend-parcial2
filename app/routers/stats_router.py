from datetime import date
from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
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


@router.get("/resumen", response_model=ResumenStats)
def obtener_resumen(
    fecha_desde: Optional[date] = Query(None, description="Filtro inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtro fin (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_resumen(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@router.get("/ventas-semanales", response_model=VentasSemanalesResponse)
def obtener_ventas_semanales(
    fecha_desde: Optional[date] = Query(None, description="Filtro inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtro fin (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_ventas_semanales(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@router.get("/productos-mas-vendidos", response_model=ProductosMasVendidosResponse)
def obtener_productos_mas_vendidos(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    fecha_desde: Optional[date] = Query(None, description="Filtro inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtro fin (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_productos_mas_vendidos(
        limit=limit,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/pedidos-por-estado", response_model=PedidosPorEstadoResponse)
def obtener_pedidos_por_estado(
    fecha_desde: Optional[date] = Query(None, description="Filtro inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtro fin (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_pedidos_por_estado(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/ingresos-por-forma-pago", response_model=IngresosPorFormaPagoResponse)
def obtener_ingresos_por_forma_pago(
    fecha_desde: Optional[date] = Query(None, description="Filtro inicio (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtro fin (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = StatsService(db)
    return service.get_ingresos_por_forma_pago(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.pedido_schema import (
    PedidoCreate,
    PedidoReadWithDetalles,
    AvanceEstadoRequest
)
from app.services.pedido_service import PedidoService
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)


# Crear pedido (CLIENT)
@router.post("/", response_model=PedidoReadWithDetalles, status_code=201)
def crear_pedido(
    datos: PedidoCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("CLIENT", "ADMIN"))
):
    service = PedidoService(db)
    return service.crear_pedido(current_user.id, datos)


# Listar pedidos (CLIENT ve los suyos, ADMIN/PEDIDOS ven todos)
@router.get("/")
def listar_pedidos(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    estado_id: Optional[int] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("CLIENT", "ADMIN", "PEDIDOS"))
):
    service = PedidoService(db)
    return service.listar_pedidos(
        current_user.id,
        current_user.tiene_rol("CLIENT"),
        limit,
        offset,
        estado_id=estado_id
    )


# Obtener pedido por ID
@router.get("/{pedido_id}", response_model=PedidoReadWithDetalles)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("CLIENT", "ADMIN", "PEDIDOS"))
):
    service = PedidoService(db)
    return service.obtener_pedido(pedido_id)


# Avanzar estado (ADMIN y PEDIDOS)
@router.patch("/{pedido_id}/estado")
def avanzar_estado(
    pedido_id: int,
    datos: AvanceEstadoRequest,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN", "PEDIDOS"))
):
    service = PedidoService(db)
    return service.avanzar_estado(pedido_id, datos.estado_id)


# Cancelar pedido (CLIENT - solo los suyos)
@router.patch("/{pedido_id}/cancelar")
def cancelar_pedido(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("CLIENT", "ADMIN"))
):
    service = PedidoService(db)
    return service.cancelar_pedido(pedido_id, current_user.id)


# Obtener historial de estados (audit trail)
@router.get("/{pedido_id}/historial")
def obtener_historial(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("CLIENT", "ADMIN", "PEDIDOS"))
):
    service = PedidoService(db)
    return service.obtener_historial(pedido_id)

from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session

from app.db.database import get_session

from app.schemas.pedido_schema import (
    PedidoCreate,
    PedidoReadWithDetails,
    AvanceEstadoRequest
)

from app.services.pedido_service import PedidoService

from app.auth.permissions import require_roles
from app.models.usuario import Usuario

from app.core.unit_of_work import UnitOfWork
from app.core.ws_manager import ws_manager

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)


# Crear pedido (CLIENT)
@router.post(
    "/",
    response_model=PedidoReadWithDetails,
    status_code=201
)
def crear_pedido(
    datos: PedidoCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("CLIENT", "ADMIN")
    )
):

    service = PedidoService(db, ws_manager)

    with UnitOfWork(db):

        pedido = service.crear_pedido(
            current_user.id,
            datos
        )

    # Broadcast WebSocket DESPUÉS del commit del UoW
    service.flush_events()

    db.refresh(pedido)

    return pedido


# Listar pedidos
@router.get(
    "/",
    response_model=list[PedidoReadWithDetails],
    summary="Listar pedidos"
)
def listar_pedidos(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    estado_codigo: Optional[str] = Query(
        None,
        description="Filtrar por estado"
    ),
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("CLIENT", "ADMIN", "PEDIDOS")
    )
):

    service = PedidoService(db)

    return service.listar_pedidos(
        current_user.id,
        current_user.tiene_rol("CLIENT"),
        limit,
        offset,
        estado_codigo=estado_codigo
    )


# Obtener pedido por ID
@router.get(
    "/{pedido_id}",
    response_model=PedidoReadWithDetails,
    summary="Obtener pedido por ID"
)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("CLIENT", "ADMIN", "PEDIDOS")
    )
):

    service = PedidoService(db)

    return service.obtener_pedido(
        pedido_id
    )


# Avanzar estado
@router.patch(
    "/{pedido_id}/estado",
    summary="Avanzar estado de un pedido"
)
def avanzar_estado(
    pedido_id: int,
    datos: AvanceEstadoRequest,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("ADMIN", "PEDIDOS")
    )
):

    service = PedidoService(db, ws_manager)

    with UnitOfWork(db):

        pedido = service.avanzar_estado(
            pedido_id,
            datos.estado_codigo,
            current_user.id
        )

    # Broadcast WebSocket DESPUÉS del commit del UoW
    service.flush_events()

    db.refresh(pedido)

    return pedido


# Cancelar pedido
@router.patch(
    "/{pedido_id}/cancelar",
    summary="Cancelar un pedido"
)
def cancelar_pedido(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("CLIENT", "ADMIN")
    )
):

    service = PedidoService(db, ws_manager)

    with UnitOfWork(db):

        pedido = service.cancelar_pedido(
            pedido_id,
            current_user.id
        )

    # Broadcast WebSocket DESPUÉS del commit del UoW
    service.flush_events()

    db.refresh(pedido)

    return pedido


# Obtener historial de estados
@router.get(
    "/{pedido_id}/historial",
    summary="Obtener historial de estados de un pedido"
)
def obtener_historial(
    pedido_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("CLIENT", "ADMIN", "PEDIDOS")
    )
):

    service = PedidoService(db)

    return service.obtener_historial(
        pedido_id
    )
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlmodel import Session

from app.auth.permissions import require_roles
from app.db.database import get_session

from app.models.usuario import Usuario

from app.schemas.pago_schema import (
    PagoCreate,
    PagoRead
)

from app.services.pago_service import (
    PagoService
)

from app.core.unit_of_work import UnitOfWork


router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)


@router.post(
    "/",
    response_model=PagoRead,
    status_code=201
)
def registrar_pago(
    datos: PagoCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = PagoService(db)

        pago = service.registrar_pago(
            datos
        )

        db.refresh(pago)

        return pago


@router.get(
    "/",
    response_model=list[PagoRead]
)
def listar_pagos(
    pedido_id: Optional[int] = Query(
        None,
        description="Filtrar por pedido"
    ),
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(
        require_roles("ADMIN", "PEDIDOS")
    )
):

    service = PagoService(db)

    if pedido_id:
        return service.listar_por_pedido(
            pedido_id
        )

    return service.listar_todos()
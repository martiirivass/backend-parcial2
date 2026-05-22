from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.pago_schema import PagoCreate, PagoRead
from app.services.pago_service import PagoService
from app.auth.permissions import require_roles
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)


@router.post("/", response_model=PagoRead, status_code=201)
def registrar_pago(
    datos: PagoCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN"))
):
    service = PagoService(db)
    return service.registrar_pago(datos)


@router.get("/", response_model=list[PagoRead])
def listar_pagos(
    pedido_id: Optional[int] = Query(None, description="Filtrar por pedido"),
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN", "PEDIDOS"))
):
    service = PagoService(db)
    if pedido_id:
        return service.listar_por_pedido(pedido_id)
    return service.listar_todos()

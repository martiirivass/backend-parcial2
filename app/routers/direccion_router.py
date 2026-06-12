from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.direccion_schema import (
    DireccionEntregaCreate,
    DireccionEntregaUpdate,
    DireccionEntregaRead,
)

from app.services.direccion_service import DireccionEntregaService
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from app.core.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/direcciones-entrega",
    tags=["Direcciones de Entrega"]
)


@router.post("/", response_model=DireccionEntregaRead, status_code=201)
def crear(
    datos: DireccionEntregaCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    with UnitOfWork(db):

        service = DireccionEntregaService(db)

        direccion = service.crear_direccion(
            current_user.id,
            datos
        )

    db.refresh(direccion)

    return direccion


@router.get("/", response_model=list[DireccionEntregaRead])
def listar(
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    service = DireccionEntregaService(db)

    return service.listar_direcciones(current_user.id)


@router.get("/{direccion_id}", response_model=DireccionEntregaRead)
def obtener(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    service = DireccionEntregaService(db)

    return service.obtener_direccion(
        direccion_id,
        current_user.id
    )


@router.put("/{direccion_id}", response_model=DireccionEntregaRead)
def actualizar(
    direccion_id: int,
    datos: DireccionEntregaUpdate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    with UnitOfWork(db):

        service = DireccionEntregaService(db)

        direccion = service.actualizar_direccion(
            direccion_id,
            current_user.id,
            datos
        )

        db.refresh(direccion)

        return direccion


@router.delete("/{direccion_id}", status_code=204)
def eliminar(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):

    with UnitOfWork(db):

        service = DireccionEntregaService(db)

        service.eliminar_direccion(
            direccion_id,
            current_user.id
        )

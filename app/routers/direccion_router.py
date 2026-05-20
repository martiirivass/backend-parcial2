from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.direccion_schema import (
    DireccionCreate,
    DireccionUpdate,
    DireccionRead
)
from app.services.direccion_service import DireccionService
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/direcciones",
    tags=["Direcciones"]
)


# Crear direccion
@router.post("/", response_model=DireccionRead, status_code=201)
def crear(
    datos: DireccionCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionService(db)
    return service.crear_direccion(current_user.id, datos)


# Listar mis direcciones
@router.get("/")
def listar(
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionService(db)
    return service.listar_direcciones(current_user.id)


# Obtener direccion
@router.get("/{direccion_id}", response_model=DireccionRead)
def obtener(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionService(db)
    return service.obtener_direccion(direccion_id, current_user.id)


# Actualizar direccion
@router.put("/{direccion_id}", response_model=DireccionRead)
def actualizar(
    direccion_id: int,
    datos: DireccionUpdate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionService(db)
    return service.actualizar_direccion(direccion_id, current_user.id, datos)


# Marcar como principal
@router.patch("/{direccion_id}/principal", response_model=DireccionRead)
def marcar_principal(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionService(db)
    return service.marcar_principal(direccion_id, current_user.id)


# Eliminar direccion (soft delete)
@router.delete("/{direccion_id}", status_code=204)
def eliminar(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionService(db)
    service.eliminar_direccion(direccion_id, current_user.id)

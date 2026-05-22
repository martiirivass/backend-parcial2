from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.direccion_schema import (
    DireccionEntregaCreate,
    DireccionEntregaUpdate,
    DireccionEntregaRead,
)
from app.services.direccion_service import DireccionEntregaService
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/direcciones-entrega",
    tags=["Direcciones de Entrega"]
)


# Crear direccion de entrega
@router.post("/", response_model=DireccionEntregaRead, status_code=201)
def crear(
    datos: DireccionEntregaCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionEntregaService(db)
    return service.crear_direccion(current_user.id, datos)


# Listar mis direcciones de entrega
@router.get("/")
def listar(
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionEntregaService(db)
    return service.listar_direcciones(current_user.id)


# Obtener direccion de entrega
@router.get("/{direccion_id}", response_model=DireccionEntregaRead)
def obtener(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionEntregaService(db)
    return service.obtener_direccion(direccion_id, current_user.id)


# Actualizar direccion de entrega
@router.put("/{direccion_id}", response_model=DireccionEntregaRead)
def actualizar(
    direccion_id: int,
    datos: DireccionEntregaUpdate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionEntregaService(db)
    return service.actualizar_direccion(direccion_id, current_user.id, datos)


# Eliminar direccion de entrega (soft delete)
@router.delete("/{direccion_id}", status_code=204)
def eliminar(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    service = DireccionEntregaService(db)
    service.eliminar_direccion(direccion_id, current_user.id)

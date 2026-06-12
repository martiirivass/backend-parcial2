<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
=======
from fastapi import APIRouter, Depends
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.direccion_schema import (
    DireccionEntregaCreate,
    DireccionEntregaUpdate,
    DireccionEntregaRead,
)
<<<<<<< HEAD
from app.services.direccion_service import DireccionEntregaService
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.models.usuario import Usuario
=======

from app.services.direccion_service import DireccionEntregaService
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from app.core.unit_of_work import UnitOfWork
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

router = APIRouter(
    prefix="/direcciones-entrega",
    tags=["Direcciones de Entrega"]
)


<<<<<<< HEAD
# Crear direccion de entrega
=======
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
@router.post("/", response_model=DireccionEntregaRead, status_code=201)
def crear(
    datos: DireccionEntregaCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
<<<<<<< HEAD
    service = DireccionEntregaService(db)
    return service.crear_direccion(current_user.id, datos)


# Listar mis direcciones de entrega
@router.get("/")
=======

    with UnitOfWork(db):

        service = DireccionEntregaService(db)

        direccion = service.crear_direccion(
            current_user.id,
            datos
        )

        db.refresh(direccion)

        return direccion


@router.get("/", response_model=list[DireccionEntregaRead])
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
def listar(
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
<<<<<<< HEAD
    service = DireccionEntregaService(db)
    return service.listar_direcciones(current_user.id)


# Obtener direccion de entrega
=======

    service = DireccionEntregaService(db)

    return service.listar_direcciones(current_user.id)


>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
@router.get("/{direccion_id}", response_model=DireccionEntregaRead)
def obtener(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
<<<<<<< HEAD
    service = DireccionEntregaService(db)
    return service.obtener_direccion(direccion_id, current_user.id)


# Actualizar direccion de entrega
=======

    service = DireccionEntregaService(db)

    return service.obtener_direccion(
        direccion_id,
        current_user.id
    )


>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
@router.put("/{direccion_id}", response_model=DireccionEntregaRead)
def actualizar(
    direccion_id: int,
    datos: DireccionEntregaUpdate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
<<<<<<< HEAD
    service = DireccionEntregaService(db)
    return service.actualizar_direccion(direccion_id, current_user.id, datos)


# Eliminar direccion de entrega (soft delete)
=======

    with UnitOfWork(db):

        service = DireccionEntregaService(db)

        direccion = service.actualizar_direccion(
            direccion_id,
            current_user.id,
            datos
        )

        db.refresh(direccion)

        return direccion


>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
@router.delete("/{direccion_id}", status_code=204)
def eliminar(
    direccion_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
<<<<<<< HEAD
    service = DireccionEntregaService(db)
    service.eliminar_direccion(direccion_id, current_user.id)
=======

    with UnitOfWork(db):

        service = DireccionEntregaService(db)

        service.eliminar_direccion(
            direccion_id,
            current_user.id
        )
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

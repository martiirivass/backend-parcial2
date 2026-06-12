from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlmodel import Session

from app.db.database import get_session

from app.schemas.admin_schema import (
    AdminUserUpdate,
    AdminUserRead,
    AdminUsersListResponse
)

from app.auth.permissions import (
    require_roles
)

from app.services.admin_service import AdminService
from app.core.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get(
    "/usuarios",
    response_model=AdminUsersListResponse
)
def listar_usuarios(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    rol_codigo: Optional[str] = None,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    service = AdminService(db)

    return service.listar_usuarios(
        limit,
        offset,
        rol_codigo=rol_codigo
    )


@router.get(
    "/usuarios/{usuario_id}",
    response_model=AdminUserRead
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    service = AdminService(db)

    return service.obtener_usuario(
        usuario_id
    )


@router.put(
    "/usuarios/{usuario_id}",
    response_model=AdminUserRead
)
def actualizar_usuario(
    usuario_id: int,
    datos: AdminUserUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    service = AdminService(db)

    with UnitOfWork(db):

        usuario = service.actualizar_usuario(
            usuario_id,
            datos
        )

    db.refresh(usuario)

    return usuario


@router.delete(
    "/usuarios/{usuario_id}",
    status_code=204
)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    service = AdminService(db)

    with UnitOfWork(db):

        service.eliminar_usuario(
            usuario_id
        )


@router.patch(
    "/usuarios/{usuario_id}/restore",
    response_model=AdminUserRead
)
def restaurar_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    service = AdminService(db)

    with UnitOfWork(db):

        usuario = service.restaurar_usuario(
            usuario_id
        )

    db.refresh(usuario)

    return usuario

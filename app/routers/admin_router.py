from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlmodel import (
    Session,
    select
)

from app.db.database import get_session

from app.schemas.admin_schema import (
    AdminUserUpdate,
    AdminUserRead,
    AdminUsersListResponse
)

from app.auth.permissions import (
    require_roles
)

from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.models.rol import Rol

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

    statement = select(Usuario)

    if rol_codigo:
        statement = statement.join(
            UsuarioRol
        ).where(
            UsuarioRol.rol_codigo == rol_codigo
        )

    usuarios = db.exec(statement).all()

    return {
        "data": usuarios[offset: offset + limit],
        "total": len(usuarios)
    }


@router.get(
    "/usuarios/{usuario_id}",
    response_model=AdminUserRead
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    usuario = db.get(
        Usuario,
        usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario


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

    usuario = db.get(
        Usuario,
        usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    update_data = datos.model_dump(
        exclude_unset=True
    )

    if "rol_ids" in update_data:

        roles = []

        for rid in update_data["rol_ids"]:

            rol = db.get(
                Rol,
                rid
            )

            if rol:
                roles.append(rol)

        usuario.roles = roles

        del update_data["rol_ids"]

    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.add(usuario)

    db.commit()

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

    usuario = db.get(
        Usuario,
        usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario.deleted_at = datetime.now(
        timezone.utc
    )

    db.add(usuario)

    db.commit()


@router.patch(
    "/usuarios/{usuario_id}/restore",
    response_model=AdminUserRead
)
def restaurar_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):

    usuario = db.get(
        Usuario,
        usuario_id
    )

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario.deleted_at = None

    db.add(usuario)

    db.commit()

    db.refresh(usuario)

    return usuario
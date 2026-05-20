from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session, select

from app.db.database import get_session
from app.schemas.admin_schema import AdminUserUpdate, AdminUserRead
from app.auth.permissions import require_roles
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# Listar usuarios (solo ADMIN)
@router.get("/usuarios")
def listar_usuarios(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    rol_id: Optional[int] = Query(None, description="Filtrar por rol"),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    statement = select(Usuario)

    if rol_id is not None:
        statement = statement.where(Usuario.rol_id == rol_id)

    # Clientes deleted_at is None o no (depende si mostramos borrados)
    # Por ahora mostramos todos menos los fisicamente eliminados
    usuarios = db.exec(statement).all()

    return {
        "data": usuarios[offset: offset + limit],
        "total": len(usuarios)
    }


# Obtener usuario por ID (solo ADMIN)
@router.get("/usuarios/{usuario_id}")
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# Actualizar usuario (solo ADMIN)
@router.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    datos: AdminUserUpdate,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    from fastapi import HTTPException

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = datos.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


# Soft delete de usuario (solo ADMIN)
@router.delete("/usuarios/{usuario_id}", status_code=204)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    from datetime import datetime, timezone
    from fastapi import HTTPException

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.deleted_at = datetime.now(timezone.utc)
    db.add(usuario)
    db.commit()

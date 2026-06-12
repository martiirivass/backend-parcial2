from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.db.database import get_session
from app.models.usuario_rol_model import UsuarioRol


def require_roles(*allowed_roles):
    def validator(
        current_user = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        user_role_codes = session.exec(
            select(UsuarioRol.rol_codigo).where(
                UsuarioRol.usuario_id == current_user.id
            )
        ).all()

        if not any(rol in allowed_roles for rol in user_role_codes):
            raise HTTPException(
                status_code=403,
                detail="Sin permisos"
            )

        return current_user

    return validator

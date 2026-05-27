from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.db.database import get_session
from app.models.usuario_rol_model import UsuarioRol


def require_roles(*allowed_roles): #Dependencia reutilizable para proteger endpoints segun roles

    def validator(
        current_user = Depends(get_current_user), #usuario actual
        session: Session = Depends(get_session) #conexion con la bd
    ):

        # Consultar roles del usuario vía UsuarioRol (N:N)
        user_role_codes = session.exec(
            select(UsuarioRol.rol_codigo).where(
                UsuarioRol.usuario_id == current_user.id
            )
        ).all()

        #pregunta si alguno de los roles del usuario esta permitido
        if not any(rol in allowed_roles for rol in user_role_codes):
            raise HTTPException(
                status_code=403, #403 autenticado pero sin permisos
                detail="Sin permisos"
            )

        return current_user #Si tiene permisos devuelve usuario autenticado

    return validator #devuelve la funcion como dependencia reutilizable

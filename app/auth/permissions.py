from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user


def require_roles(*allowed_roles):

    def validator(
        current_user = Depends(
            get_current_user
        )
    ):
        # Verifico si el usuario tiene ALGUNO de los roles permitidos
        for rol in current_user.roles:
            if rol.codigo in allowed_roles:
                return current_user

        raise HTTPException(
            status_code=403,
            detail="Sin permisos"
        )

    return validator

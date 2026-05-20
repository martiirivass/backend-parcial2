from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user


def require_roles(*allowed_roles):

    def validator(
        current_user = Depends(
            get_current_user
        )
    ):

        if current_user.rol.codigo not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Sin permisos"
            )

        return current_user

    return validator
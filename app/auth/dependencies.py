from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException
from sqlmodel import Session

from app.auth.security import (
    SECRET_KEY,
    ALGORITHM
)

from app.db.database import get_session
from app.models.usuario import Usuario


def get_current_user(
    access_token: Annotated[
        str | None,
        Cookie()
    ] = None,
    session: Session = Depends(get_session)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No autenticado"
        )

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

    except:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    user = session.get(
        Usuario,
        int(user_id)
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return user
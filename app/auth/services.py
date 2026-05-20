from fastapi import HTTPException
from sqlmodel import Session, select

from app.auth.security import (
    verify_password,
    create_access_token
)

from app.models.usuario import Usuario


def login_user(
    email: str,
    password: str,
    session: Session
):
    user = session.exec(
        select(Usuario).where(
            Usuario.email == email
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    if not verify_password(
        password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    token = create_access_token({
        "sub": str(user.id)
    })

    return token
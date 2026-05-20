from fastapi import HTTPException
from sqlmodel import Session, select

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol


def register_user(
    nombre: str,
    email: str,
    password: str,
    session: Session
):
    existing_user = session.exec(
        select(Usuario).where(
            Usuario.email == email
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="El email ya existe"
        )

    user = Usuario(
        nombre=nombre,
        email=email,
        password=hash_password(password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    client_role = session.exec(
        select(Rol).where(
            Rol.codigo == "CLIENT"
        )
    ).first()

    user_role = UsuarioRol(
        usuario_id=user.id,
        rol_id=client_role.id
    )

    session.add(user_role)
    session.commit()

    return user


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
from fastapi import HTTPException
from sqlmodel import Session, select

from app.auth.security import (
    verify_password,
    create_access_token,
    hash_password
)

from app.models.usuario import Usuario
from app.models.rol import Rol


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


def register_user(
    nombre: str,
    email: str,
    password: str,
    session: Session
):
    # Verificar si el email ya esta registrado
    existente = session.exec(
        select(Usuario).where(Usuario.email == email)
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El email ya esta registrado"
        )

    # Buscar el rol CLIENT por defecto
    rol_cliente = session.exec(
        select(Rol).where(Rol.codigo == "CLIENT")
    ).first()

    if not rol_cliente:
        raise HTTPException(
            status_code=500,
            detail="Error de configuracion: rol CLIENT no encontrado"
        )

    # Crear el usuario
    user = Usuario(
        nombre=nombre,
        apellido="",  # Opcional por ahora
        email=email,
        password=hash_password(password),
        roles=[rol_cliente]  # Asigno el rol CLIENT por defecto
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def get_me(current_user: Usuario):
    return current_user

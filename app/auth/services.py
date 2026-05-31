from fastapi import HTTPException
from sqlmodel import Session

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol

from app.repositories.auth_repository import AuthRepository


def login_user(
    email: str,
    password: str,
    session: Session
):
    auth_repository = AuthRepository(session)

    user = auth_repository.get_user_by_email(
        email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    if not verify_password(
        password,
        user.password_hash
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
    auth_repository = AuthRepository(session)

    # Verificar email existente
    existente = auth_repository.get_user_by_email(
        email
    )

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El email ya esta registrado"
        )

    # Obtener rol CLIENT
    rol_cliente = auth_repository.get_client_role()

    if not rol_cliente:
        raise HTTPException(
            status_code=500,
            detail="Error de configuración: rol CLIENT no encontrado"
        )

    # Crear usuario
    user = Usuario(
        nombre=nombre,
        apellido="",
        email=email,
        password_hash=hash_password(password),
    )

    auth_repository.add(user)

    # Necesario para obtener el ID antes del commit
    session.flush()

    # Relación usuario-rol
    usuario_rol = UsuarioRol(
        usuario_id=user.id,
        rol_codigo=rol_cliente.codigo
    )

    auth_repository.add_user_role(
        usuario_rol
    )

    return user


def get_me(current_user: Usuario):
    return current_user
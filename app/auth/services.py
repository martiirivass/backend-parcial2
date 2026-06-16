from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.models.tipo_documento_model import TipoDocumento

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
    session: Session,
    tipo_documento_codigo: Optional[str] = None,
    numero_documento: Optional[str] = None,
):

    auth_repository = AuthRepository(session)

    existente = auth_repository.get_user_by_email(email)

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El email ya esta registrado"
        )

    rol_cliente = auth_repository.get_client_role()

    if not rol_cliente:
        raise HTTPException(
            status_code=500,
            detail="Error de configuración: rol CLIENT no encontrado"
        )

    # Resolver tipo de documento si se envió
    tipo_documento_id = None
    if tipo_documento_codigo:
        td = session.exec(
            select(TipoDocumento).where(TipoDocumento.codigo == tipo_documento_codigo)
        ).first()
        if td:
            tipo_documento_id = td.id

    user = Usuario(
        nombre=nombre,
        apellido="",
        email=email,
        password_hash=hash_password(password),
        tipo_documento_id=tipo_documento_id,
        numero_documento=numero_documento,
    )

    auth_repository.add(user)

    session.flush()

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

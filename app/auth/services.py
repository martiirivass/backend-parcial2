from datetime import datetime, timedelta, UTC
import secrets
from typing import Optional

import jwt
from fastapi import HTTPException
from sqlmodel import Session, select

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    hash_token,
    SECRET_KEY,
    ALGORITHM,
)

from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.models.tipo_documento_model import TipoDocumento
from app.models.refresh_token_model import RefreshToken

from app.repositories.auth_repository import AuthRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository


def _create_refresh_token(session: Session, usuario_id: int) -> str:
    raw = secrets.token_urlsafe(64)
    refresh = RefreshToken(
        usuario_id=usuario_id,
        token_hash=hash_token(raw),
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    session.add(refresh)
    return raw


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
    apellido: str,
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
        apellido=apellido,
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


def refresh_user_token(session: Session, refresh_token_str: str) -> tuple[str, str]:
    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="Refresh token requerido")

    repo = RefreshTokenRepository(session)
    stored = repo.get_valid_token(hash_token(refresh_token_str))

    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    stored.revoked_at = datetime.now(UTC)
    session.add(stored)

    new_token = create_access_token({"sub": str(stored.usuario_id)})
    new_raw = _create_refresh_token(session, stored.usuario_id)

    return new_token, new_raw


def revoke_user_tokens(session: Session, usuario_id: int) -> None:
    repo = RefreshTokenRepository(session)
    repo.revoke_user_tokens(usuario_id)

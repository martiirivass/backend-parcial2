from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class RefreshTokenCreate(SQLModel):
    """Esquema para crear un registro de token de refresco."""
    usuario_id: int
    token: str
    expires_at: datetime


class RefreshTokenRead(SQLModel):
    """Modelo de lectura para un token de refresco con información de revocación."""
    id: int
    usuario_id: int
    token: str
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    created_at: datetime

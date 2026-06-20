from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel


class AdminUserUpdate(SQLModel):
    """Esquema para que el administrador actualice el perfil y roles de un usuario."""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = None
    rol_ids: Optional[List[str]] = None


class AdminUserRead(SQLModel):
    """Modelo de lectura para un usuario en el panel de administración."""
    id: int
    nombre: str
    apellido: str
    email: str
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = None
    deleted_at: Optional[datetime] = None


class AdminUsersListResponse(SQLModel):
    """Respuesta paginada para la lista de usuarios del panel de administración."""
    data: List[AdminUserRead]
    total: int
    page: int
    size: int
    pages: int

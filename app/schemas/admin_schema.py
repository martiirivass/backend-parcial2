from typing import Optional, List

from sqlmodel import SQLModel


class AdminUserUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = None
    rol_ids: Optional[List[str]] = None


class AdminUserRead(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = None
    deleted_at: Optional[str] = None


class AdminUsersListResponse(SQLModel):
    data: List[AdminUserRead]
    total: int

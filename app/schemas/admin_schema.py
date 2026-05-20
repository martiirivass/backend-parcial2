from typing import Optional
from sqlmodel import SQLModel


class AdminUserUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    rol_id: Optional[int] = None


class AdminUserRead(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    rol_id: Optional[int] = None
    deleted_at: Optional[str] = None

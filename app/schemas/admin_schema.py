from typing import Optional, List
from sqlmodel import SQLModel


class AdminUserUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    rol_ids: Optional[List[int]] = None


class AdminUserRead(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    deleted_at: Optional[str] = None

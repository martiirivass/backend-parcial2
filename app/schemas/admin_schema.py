from typing import Optional, List
<<<<<<< HEAD
=======

>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b
from sqlmodel import SQLModel


class AdminUserUpdate(SQLModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    rol_ids: Optional[List[str]] = None


class AdminUserRead(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    deleted_at: Optional[str] = None
<<<<<<< HEAD
=======


class AdminUsersListResponse(SQLModel):
    data: List[AdminUserRead]
    total: int
>>>>>>> 53b31fe58213626f62945aebb5ef0d515140b85b

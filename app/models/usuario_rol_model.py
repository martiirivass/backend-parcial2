from typing import Optional
from sqlmodel import SQLModel, Field


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuarios_roles"

    usuario_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="usuarios.id"
    )
    rol_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="roles.id"
    )

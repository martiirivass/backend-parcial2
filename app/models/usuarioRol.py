from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuarios_roles"

    id: int | None = Field(default=None, primary_key=True)

    usuario_id: int = Field(
        foreign_key="usuarios.id",
        nullable=False
    )

    rol_id: int = Field(
        foreign_key="roles.id",
        nullable=False
    )

    usuario: Optional["Usuario"] = Relationship(
        back_populates="roles"
    )

    rol: Optional["Rol"] = Relationship(
        back_populates="usuarios"
    )
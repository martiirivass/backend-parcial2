from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.rol import Rol


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: int = Field(
        default=None, primary_key=True, foreign_key="usuarios.id"
    )
    rol_codigo: str = Field(
        default=None, primary_key=True, foreign_key="roles.codigo", max_length=20
    )
    asignado_por: Optional[int] = Field(
        default=None, foreign_key="usuarios.id"
    )

    usuario: "Usuario" = Relationship(back_populates="usuario_roles")
    rol: "Rol" = Relationship(back_populates="usuario_roles")

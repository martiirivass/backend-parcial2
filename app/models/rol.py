from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario_rol_model import UsuarioRol


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    codigo: str = Field(default=None, primary_key=True, max_length=20)
    nombre: str
    descripcion: Optional[str] = None

    usuario_roles: List["UsuarioRol"] = Relationship(back_populates="rol")

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario_rol_model import UsuarioRol
    from app.models.refresh_token_model import RefreshToken
    from app.models.direccion_model import Direccion


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    email: str
    password: str  # Hash de bcrypt

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relación N:N con roles a través de UsuarioRol
    usuario_roles: List["UsuarioRol"] = Relationship(back_populates="usuario")

    # Relaciones
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="usuario")
    direcciones: List["Direccion"] = Relationship(back_populates="usuario")

    @property
    def roles(self):
        return [ur.rol for ur in self.usuario_roles] if self.usuario_roles else []

    def tiene_rol(self, codigo: str) -> bool:
        return any(r.codigo == codigo for r in self.roles)

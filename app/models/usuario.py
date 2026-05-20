from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from app.models.usuario_rol_model import UsuarioRol

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido
    from app.models.direccion_model import Direccion
    from app.models.rol import Rol


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    email: str
    password: str  # Hash de bcrypt
    
    # Soft delete para gestión de usuarios
    deleted_at: Optional[datetime] = Field(default=None)

    # Relacion N:N con roles (UsuarioRol)
    roles: List["Rol"] = Relationship(
        back_populates="usuarios",
        link_model=UsuarioRol
    )

    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
    direcciones: List["Direccion"] = Relationship(back_populates="usuario")

    # Helper para saber si tiene un rol
    def tiene_rol(self, codigo: str) -> bool:
        return any(r.codigo == codigo for r in self.roles)

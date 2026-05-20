from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido_model import Pedido
    from app.models.direccion_model import Direccion


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    email: str
    password: str # Necesario para guardar el hash de bcrypt
    
    # Soft delete para gestión de usuarios
    deleted_at: Optional[datetime] = Field(default=None)

    rol_id: Optional[int] = Field(default=None, foreign_key="roles.id")
    rol: Optional["Rol"] = Relationship(back_populates="usuarios")

    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
    direcciones: List["Direccion"] = Relationship(back_populates="usuario")
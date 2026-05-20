from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


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
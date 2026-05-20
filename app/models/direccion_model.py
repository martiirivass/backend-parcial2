from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Direccion(SQLModel, table=True):
    __tablename__ = "direcciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    alias: str = Field(default="Casa")  # Ej: "Casa", "Trabajo"
    direccion: str
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    principal: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)

    usuario: "Usuario" = Relationship(back_populates="direcciones")

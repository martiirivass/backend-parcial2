from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class DireccionEntrega(SQLModel, table=True):
    __tablename__ = "direcciones_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    calle: str = Field(max_length=200)
    ciudad: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=20)
    pais: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)

    usuario: "Usuario" = Relationship(back_populates="direcciones")

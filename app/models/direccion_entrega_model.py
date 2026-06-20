from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index, text

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class DireccionEntrega(SQLModel, table=True):
    __tablename__ = "direcciones_entrega"
    __table_args__ = (
        Index(
            "ix_direccion_entrega_principal_unica",
            "usuario_id",
            unique=True,
            postgresql_where=text("es_principal = true")
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    alias: Optional[str] = Field(default=None, max_length=50)
    linea1: str
    linea2: Optional[str] = Field(default=None)
    ciudad: str = Field(max_length=100)
    provincia: Optional[str] = Field(default=None, max_length=100)
    codigo_postal: Optional[str] = Field(default=None, max_length=10)
    latitud: Optional[float] = Field(default=None)   # DECIMAL(9,6)
    longitud: Optional[float] = Field(default=None)  # DECIMAL(9,6)
    es_principal: bool = Field(default=False)

    # Timestamps y soft delete
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    usuario: "Usuario" = Relationship(back_populates="direcciones")

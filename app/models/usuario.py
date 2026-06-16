from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario_rol_model import UsuarioRol
    from app.models.refresh_token_model import RefreshToken
    from app.models.direccion_entrega_model import DireccionEntrega
    from app.models.tipo_documento_model import TipoDocumento


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=80)
    apellido: str = Field(max_length=80)
    email: str = Field(max_length=254, unique=True)
    celular: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=60)  # bcrypt hash

    # Documento
    tipo_documento_id: Optional[int] = Field(default=None, foreign_key="tipos_documento.id")
    numero_documento: Optional[str] = Field(default=None, max_length=20)

    # Soft delete
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    # Relación N:N con roles a través de UsuarioRol
    usuario_roles: List["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"}
    )

    # Relaciones
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="usuario")
    direcciones: List["DireccionEntrega"] = Relationship(back_populates="usuario")

    @property
    def roles(self):
        return [ur.rol for ur in self.usuario_roles] if self.usuario_roles else []

    def tiene_rol(self, codigo: str) -> bool:
        return any(r.codigo == codigo for r in self.roles)

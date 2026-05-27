from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

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
    asignado_por_id: Optional[int] = Field(
        default=None, foreign_key="usuarios.id"
    )
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    usuario: "Usuario" = Relationship(
        back_populates="usuario_roles",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"}
    )
    rol: "Rol" = Relationship(back_populates="usuario_roles")

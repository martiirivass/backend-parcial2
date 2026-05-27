from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    token_hash: str = Field(max_length=64, unique=True)  # SHA-256 hash
    expires_at: datetime
    revoked_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    usuario: "Usuario" = Relationship(back_populates="refresh_tokens")

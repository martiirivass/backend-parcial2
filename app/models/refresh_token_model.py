from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    token: str = Field(max_length=500, unique=True)
    expires_at: datetime
    revoked_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    usuario: "Usuario" = Relationship(back_populates="refresh_tokens")

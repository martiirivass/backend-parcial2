from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class RefreshTokenCreate(SQLModel):
    usuario_id: int
    token: str
    expires_at: datetime


class RefreshTokenRead(SQLModel):
    id: int
    usuario_id: int
    token: str
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    created_at: datetime

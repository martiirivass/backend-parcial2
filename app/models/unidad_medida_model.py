from typing import Optional
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidades_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50, unique=True)
    simbolo: str = Field(max_length=10, unique=True)
    tipo: str = Field(max_length=20)  # masa, volumen, unidad, area
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

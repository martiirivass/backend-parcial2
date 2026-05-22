from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel
from pydantic import field_validator


class DireccionEntregaCreate(SQLModel):
    calle: str
    ciudad: str
    codigo_postal: Optional[str] = None
    pais: str = "Argentina"

    @field_validator("calle")
    def validar_calle(cls, v):
        if not v.strip():
            raise ValueError("La calle no puede estar vacia")
        return v


class DireccionEntregaUpdate(SQLModel):
    calle: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None


class DireccionEntregaRead(SQLModel):
    id: int
    usuario_id: int
    calle: str
    ciudad: str
    codigo_postal: Optional[str] = None
    pais: str
    created_at: datetime
    updated_at: datetime

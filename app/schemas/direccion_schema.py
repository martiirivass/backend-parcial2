from typing import Optional
from sqlmodel import SQLModel
from pydantic import field_validator


class DireccionCreate(SQLModel):
    alias: str = "Casa"
    direccion: str
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None

    @field_validator("direccion")
    def validar_direccion(cls, v):
        if not v.strip():
            raise ValueError("La direccion no puede estar vacia")
        return v


class DireccionUpdate(SQLModel):
    alias: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None


class DireccionRead(SQLModel):
    id: int
    usuario_id: int
    alias: str
    direccion: str
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    principal: bool

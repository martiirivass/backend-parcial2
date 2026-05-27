from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel
from pydantic import field_validator


class DireccionEntregaCreate(SQLModel):
    alias: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: bool = False

    @field_validator("linea1")
    def validar_linea1(cls, v):
        if not v.strip():
            raise ValueError("La direccion no puede estar vacia")
        return v


class DireccionEntregaUpdate(SQLModel):
    alias: Optional[str] = None
    linea1: Optional[str] = None
    linea2: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: Optional[bool] = None


class DireccionEntregaRead(SQLModel):
    id: int
    usuario_id: int
    alias: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: bool
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    created_at: datetime
    updated_at: datetime

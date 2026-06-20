from typing import Optional
from sqlmodel import SQLModel


class UnidadMedidaBase(SQLModel):
    """Esquema base con campos comunes de unidad de medida."""
    nombre: str
    simbolo: str
    tipo: str


class UnidadMedidaCreate(UnidadMedidaBase):
    """Esquema para crear una nueva unidad de medida."""


class UnidadMedidaUpdate(SQLModel):
    """Esquema para actualizar una unidad de medida existente."""
    nombre: Optional[str] = None
    simbolo: Optional[str] = None
    tipo: Optional[str] = None


class UnidadMedidaRead(UnidadMedidaBase):
    """Modelo de lectura para una unidad de medida."""
    id: int

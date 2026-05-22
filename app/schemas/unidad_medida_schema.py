from typing import Optional
from sqlmodel import SQLModel


class UnidadMedidaBase(SQLModel):
    nombre: str
    simbolo: str
    tipo: str  # masa, volumen, unidad, area


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaUpdate(SQLModel):
    nombre: Optional[str] = None
    simbolo: Optional[str] = None
    tipo: Optional[str] = None


class UnidadMedidaRead(UnidadMedidaBase):
    id: int

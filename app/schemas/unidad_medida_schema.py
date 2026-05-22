from typing import Optional
from sqlmodel import SQLModel


class UnidadMedidaBase(SQLModel):
    nombre: str
    abreviatura: str
    descripcion: Optional[str] = None


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaUpdate(SQLModel):
    nombre: Optional[str] = None
    abreviatura: Optional[str] = None
    descripcion: Optional[str] = None


class UnidadMedidaRead(UnidadMedidaBase):
    id: int

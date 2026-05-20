from typing import Optional
from sqlmodel import SQLModel, Field


class FormaPago(SQLModel, table=True):
    __tablename__ = "formas_pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

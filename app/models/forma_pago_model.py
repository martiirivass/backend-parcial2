from typing import Optional

from sqlmodel import Field, SQLModel


class FormaPago(SQLModel, table=True):
    __tablename__ = "formas_pago"

    codigo: str = Field(default=None, primary_key=True, max_length=20)
    nombre: str = Field(max_length=50)
    descripcion: Optional[str] = None

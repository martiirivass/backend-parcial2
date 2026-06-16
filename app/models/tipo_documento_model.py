from typing import Optional

from sqlmodel import Field, SQLModel


class TipoDocumento(SQLModel, table=True):
    __tablename__ = "tipos_documento"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=20, unique=True)
    nombre: str = Field(max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=255)

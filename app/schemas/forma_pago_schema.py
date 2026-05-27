from typing import Optional
from sqlmodel import SQLModel


class FormaPagoRead(SQLModel):
    codigo: str
    descripcion: str
    habilitado: bool

from typing import Optional
from sqlmodel import SQLModel


class FormaPagoRead(SQLModel):
    """Modelo de lectura para una forma de pago."""


    codigo: str
    descripcion: str
    habilitado: bool

from typing import Optional
from sqlmodel import SQLModel


class FormaPagoRead(SQLModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

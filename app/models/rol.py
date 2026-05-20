from typing import Optional, List

from sqlmodel import Field, Relationship, SQLModel


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str # ADMIN, STOCK, PEDIDOS, CLIENT
    nombre: str

    usuarios: List["Usuario"] = Relationship(back_populates="rol")
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.rol import Rol


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    firstname: str

    lastname: str

    email: str = Field(
        unique=True,
        index=True
    )

    password: str

    is_active: bool = True

    rol_id: Optional[int] = Field(
        default=None,
        foreign_key="roles.id"
    )

    rol: Optional[Rol] = Relationship(
        back_populates="usuarios"
    )
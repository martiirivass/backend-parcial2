from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(
        unique=True,
        nullable=False
    )

    usuarios: list["Usuario"] = Relationship(
        back_populates="rol"
    )
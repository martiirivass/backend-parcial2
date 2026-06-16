from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Numeric


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="productos.id"
    )
    ingrediente_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="ingredientes.id"
    )
    cantidad: Decimal = Field(default=Decimal('1'), sa_column=Column(Numeric(10, 3)))
    unidad_medida_id: Optional[int] = Field(
        default=None, foreign_key="unidades_medida.id"
    )
    es_removible: bool = Field(default=False)

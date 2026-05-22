from typing import Optional

from sqlmodel import Field, SQLModel


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="productos.id"
    )
    ingrediente_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="ingredientes.id"
    )
    cantidad: float = Field(default=1.0)
    unidad_medida_id: Optional[int] = Field(
        default=None, foreign_key="unidades_medida.id"
    )
    es_removible: bool = Field(default=False)

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Numeric, CheckConstraint, ARRAY, Text, Integer
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente

if TYPE_CHECKING:
    from app.models.ingrediente_model import Ingrediente
    from app.models.categoria_model import Categoria


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal = Field(
        default=Decimal('0'),
        sa_column=Column(Numeric(10, 2), CheckConstraint("precio_base >= 0"))
    )
    unidad_venta_id: Optional[int] = Field(default=None, foreign_key="unidades_medida.id")
    imagenes_url: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text))
    )
    stock_cantidad: int = Field(
        default=0,
        sa_column=Column(Integer, CheckConstraint("stock_cantidad >= 0"))
    )
    disponible: bool = Field(default=True)

    # Timestamps y soft delete
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)

    # Aliases para compatibilidad con frontend
    @property
    def precio(self) -> float:
        return self.precio_base

    @property
    def imagen_url(self) -> Optional[str]:
        if self.imagenes_url and len(self.imagenes_url) > 0:
            return self.imagenes_url[0]
        return None

    # Relacion N:N con categorias
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria
    )

    # Relacion N:N con ingredientes
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos",
        link_model=ProductoIngrediente
    )

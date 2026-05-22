from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente

# Evitar importaciones circulares
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ingrediente_model import Ingrediente
    from app.models.categoria_model import Categoria


class Producto(SQLModel, table=True):
    __tablename__ = "productos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    imagen_url: Optional[str] = Field(default=None)
    stock_cantidad: int = Field(default=0)
    disponible: bool = Field(default=True)
    
    # Timestamps y soft delete
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)
    
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

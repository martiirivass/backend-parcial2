from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_categoria_model import ProductoCategoria

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.producto_model import Producto

class Categoria(SQLModel, table=True):
    __tablename__ = "categorias" 
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str 
    descripcion: Optional[str] = None
    activo: bool = True

    #Soft Delete con TIMESTAMP
    deleted_at: Optional[datetime] = Field(default=None)
    
    # Relación recursiva para subcategorías
    parent_id: Optional[int] = Field(default=None, foreign_key="categorias.id")

    parent: Optional["Categoria"] = Relationship(
        back_populates="subcategorias",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )
    subcategorias: List["Categoria"] = Relationship(
        back_populates="parent"
    )

    # NUEVA RELACIÓN N:N (Una categoría tiene muchos productos, un producto tiene muchas categorías)
    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria
    )
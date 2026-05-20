from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_category_model import ProductoCategoria

#para evitar importaciones circulares
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # importamos solo para tipado, no se ejecutan en tiempo de ejecución
    from app.models.producto_model import Producto

class Categoria(SQLModel, table=True):
    __tablename__ = "categorias" 
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str 
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)
    
    #RELACIÓN RECURSIVA PARA CATEGORIAS (SUBCATEGORIAS)
    parent_id: Optional[int] = Field(default=None, foreign_key="categorias.id")

    parent: Optional["Categoria"] = Relationship(
        back_populates="subcategorias",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )

    subcategorias: List["Categoria"] = Relationship(
        back_populates="parent"
    )

    # Relacion N:N con productos (lo que ya tenías)
    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria
    )
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_ingrediente_model import ProductoIngrediente

# Evitar importaciones circulares
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.producto_model import Producto

class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingredientes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False
    activo: bool = Field(default=True)
    
    # Relacion N:N con productos
    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model= ProductoIngrediente
    )
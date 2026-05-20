from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente

# Evitar importaciones circulares
# Estas importaciones solo se utilizan para tipado y no se ejecutan en tiempo de ejecución.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ingrediente_model import Ingrediente
    from app.models.categoria_model import Categoria
    

class Producto(SQLModel, table=True):
    __tablename__ = "productos"
    
    id: Optional[int] = Field(default=None, primary_key=True) #Campo ID autoincremental
    nombre: str  #Campo obligatorio para el nombre del producto
    descripcion: Optional[str] = None #Campo opcional para la descripción del producto
    precio: float #Campo obligatorio para el precio del producto
    activo: bool = Field(default=True)
    
    # Relacion N:N con categorias
    categorias: List["Categoria"] = Relationship( #Relación con la clase Categoria, se define como una lista de objetos Categoria
        back_populates="productos", #Indica que la relación es bidireccional y se relaciona con el atributo "productos" de la clase Categoria
        link_model=ProductoCategoria #tabla intermedia que relaciona productos y categorias
    )
    
    # Relacion N:N con ingredientes
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos",
        link_model=ProductoIngrediente
    )
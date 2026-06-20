from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel
from pydantic import field_validator # Validaciones personalizadas

# Evitar importaciones circulares
if TYPE_CHECKING:
    from app.schemas.producto_schema import ProductoRead


class CategoriaBase(SQLModel):
    """Esquema base con campos comunes de categoría."""
    nombre: str
    descripcion: Optional[str] = None

    # Validación personalizada para el nombre de la categoría
    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip(): #Evita que el nombre sea vacio o espacios en blancos
            raise ValueError("El nombre no puede estar vacío")
        return v

#Para crear categorias, reutiliza categoriaBase
class CategoriaCreate(CategoriaBase):
    """Esquema para crear una nueva categoría."""
    parent_id: Optional[int] = None

#Para actualizar categorias, todos los campos son opcionales
class CategoriaUpdate(SQLModel):
    """Esquema para actualizar una categoría existente (todos los campos opcionales)."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None

#Para leer categorias, incluye el id
class CategoriaRead(CategoriaBase):
    """Modelo de lectura para una categoría, incluye id y url de imagen."""
    id: int
    parent_id: Optional[int] = None
    imagen_url: Optional[str] = None

#Para leer categorias con sus productos relacionados
class CategoriaReadWithProductos(CategoriaRead):
    """Categoría con sus productos relacionados incluidos."""
    productos: List["ProductoRead"] = []

#Para el arbol de categorias (consulta recursiva)
class CategoriaTree(CategoriaRead):
    """Árbol jerárquico de categorías con subcategorías anidadas."""
    subcategorias: List["CategoriaTree"] = []
    

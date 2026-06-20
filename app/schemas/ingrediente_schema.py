from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel
from pydantic import field_validator

if TYPE_CHECKING:
    from app.schemas.producto_schema import ProductoRead


class IngredienteBase(SQLModel):
    """Esquema base con campos comunes de ingrediente."""
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False
    stock_cantidad: int = 0

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v


class IngredienteCreate(IngredienteBase):
    """Esquema para crear un nuevo ingrediente."""


class IngredienteUpdate(SQLModel):
    """Esquema para actualizar un ingrediente existente."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None
    stock_cantidad: Optional[int] = None


class IngredienteRead(IngredienteBase):
    """Modelo de lectura para un ingrediente."""
    id: int


class IngredienteReadWithProductos(IngredienteRead):
    """Ingrediente con sus productos relacionados."""
    productos: List["ProductoRead"] = []
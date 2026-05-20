from typing import Optional, List, TYPE_CHECKING #Evitar importaciones circulares
from sqlmodel import SQLModel #BaseModel para SQLModel
from pydantic import field_validator #Validaciones personalizadas


if TYPE_CHECKING:
    from app.schemas.cat_schema import CategoriaRead
    from app.schemas.ing_schema import IngredienteRead


class ProductoBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v
    
    @field_validator("precio")
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError("El precio no puede ser negativo o igual a 0")
        return v

class ProductoCreate(ProductoBase):
    categoria_ids: Optional[List[int]] = None
    ingrediente_ids: Optional[List[int]] = None
    
    @field_validator("categoria_ids", "ingrediente_ids")
    def validar_listas(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe enviar al menos una categoría e ingrediente")
        return v

class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    categoria_ids: Optional[List[int]] = None
    ingrediente_ids: Optional[List[int]] = None
    
    @field_validator("precio")
    def validar_precio(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        return v


class ProductoRead(ProductoBase):
    id: int


class ProductoReadWithRelations(ProductoRead):
    categorias: List["CategoriaRead"] = []
    ingredientes: List["IngredienteRead"] = []
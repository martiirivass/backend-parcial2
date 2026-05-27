from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel
from pydantic import field_validator


if TYPE_CHECKING:
    from app.schemas.categoria_schema import CategoriaRead
    from app.schemas.ingrediente_schema import IngredienteRead


class ProductoBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    unidad_venta_id: Optional[int] = None
    imagenes_url: Optional[str] = None
    stock_cantidad: int = 0
    disponible: bool = True

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v

    @field_validator("precio_base")
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
    precio_base: Optional[float] = None
    unidad_venta_id: Optional[int] = None
    imagenes_url: Optional[str] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    categoria_ids: Optional[List[int]] = None
    ingrediente_ids: Optional[List[int]] = None

    @field_validator("precio_base")
    def validar_precio(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        return v


class ProductoRead(ProductoBase):
    id: int
    precio: float  # alias via @property del modelo
    imagen_url: Optional[str] = None  # alias via @property del modelo


class ProductoReadWithRelations(ProductoRead):
    categorias: List["CategoriaRead"] = []
    ingredientes: List["IngredienteRead"] = []


class ProductoDisponibilidadUpdate(SQLModel):
    disponible: bool
    stock_cantidad: Optional[int] = None

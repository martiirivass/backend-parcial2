from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel
from pydantic import field_validator


if TYPE_CHECKING:
    from app.schemas.categoria_schema import CategoriaRead
    from app.schemas.ingrediente_schema import IngredienteRead


class ProductoBase(SQLModel):
    """Esquema base con campos comunes de producto."""
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    unidad_venta_id: Optional[int] = None
    imagenes_url: Optional[List[str]] = None
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
    """Esquema para crear un nuevo producto con relaciones de categoría e ingrediente."""
    categoria_ids: Optional[List[int]] = None
    ingrediente_ids: Optional[List[int]] = None

    @field_validator("categoria_ids", "ingrediente_ids")
    def validar_listas(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe enviar al menos una categoría e ingrediente")
        return v


class ProductoUpdate(SQLModel):
    """Esquema para actualizar un producto existente (todos los campos opcionales)."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = None
    unidad_venta_id: Optional[int] = None
    imagenes_url: Optional[List[str]] = None
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
    """Modelo de lectura para un producto con alias precio e imagen_url calculados."""
    id: int
    precio: Decimal  # alias via @property del modelo
    imagen_url: Optional[str] = None  # alias via @property del modelo
    imagen_public_id: Optional[str] = None


class ProductoReadWithRelations(ProductoRead):
    """Producto con sus categorías e ingredientes incluidos."""
    categorias: List["CategoriaRead"] = []
    ingredientes: List["IngredienteRead"] = []


class ProductoImagenesUpdate(SQLModel):
    """Esquema para actualizar las imágenes de un producto."""
    imagenes_url: List[str]

    @field_validator("imagenes_url")
    def validar_imagenes_no_vacias(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe enviar al menos una URL de imagen")
        return v


class ProductoDisponibilidadUpdate(SQLModel):
    """Esquema para alternar la disponibilidad de un producto y actualizar su stock."""
    disponible: bool
    stock_cantidad: Optional[int] = None


class ProductoIngredienteCreate(SQLModel):
    """Esquema para vincular un ingrediente a un producto con cantidad."""
    ingrediente_id: int
    cantidad: float = 1.0
    unidad_medida_id: Optional[int] = None
    es_removible: bool = False


class ProductoIngredienteRead(SQLModel):
    """Modelo de lectura para una relación producto-ingrediente."""
    producto_id: int
    ingrediente_id: int
    nombre_ingrediente: str
    es_alergeno: bool
    cantidad: float
    unidad_medida_id: Optional[int] = None
    es_removible: bool

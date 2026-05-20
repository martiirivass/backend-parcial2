from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel
from pydantic import field_validator # Validaciones personalizadas

# Evitar importaciones circulares
if TYPE_CHECKING:
    from app.schemas.producto_schema import ProductoRead


class IngredienteBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False

    # Validación personalizada para el nombre del ingrediente
    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip(): #Evita que el nombre sea vacio o espacios en blancos
            raise ValueError("El nombre no puede estar vacío")
        return v

#Para crear ingredientes, reutiliza ingredienteBase
class IngredienteCreate(IngredienteBase):
    pass

#Para actualizar ingredientes, todos los campos son opcionales
class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None

#Para leer ingredientes, incluye el id
class IngredienteRead(IngredienteBase):
    id: int

#Para leer ingredientes con sus productos relacionados
class IngredienteReadWithProductos(IngredienteRead):
    productos: List["ProductoRead"] = []
    

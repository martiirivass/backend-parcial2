from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from app.models.producto_ingrediente_model import ProductoIngrediente

# Evitar importaciones circulares
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.producto_model import Producto

class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingredientes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = None
    es_alergeno: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relacion N:N con productos
    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=ProductoIngrediente
    )

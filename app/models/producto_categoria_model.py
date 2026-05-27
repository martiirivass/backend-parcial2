from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"
    
    producto_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="productos.id"
    )
    categoria_id: Optional[int] = Field(
        default=None, primary_key=True, foreign_key="categorias.id"
    )
    es_principal: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

from typing import Optional
from sqlmodel import SQLModel, Field

class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"
    
    producto_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="productos.id") #clave foranea que referencia al id de la tabla productos
    categoria_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="categorias.id") #clave foranea que referencia al id de la tabla categorias
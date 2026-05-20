from typing import Optional
from sqlmodel import SQLModel, Field

class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"
    
    producto_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="productos.id") #clave foranea que referencia al id de la tabla productos
    ingrediente_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="ingredientes.id") #clave foranea que referencia al id de la tabla ingredientes
from sqlmodel import SQLModel
from app.db.database import engine

from app.models.producto_model import Producto
from app.models.categoria_model import Categoria
from app.models.ingrediente_model import Ingrediente
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente

def init_db():
    SQLModel.metadata.create_all(engine)
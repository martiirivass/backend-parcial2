from sqlmodel import SQLModel
from app.db.database import engine

from app.models.producto_model import Producto
from app.models.category_model import Categoria
from app.models.ingredient_model import Ingrediente
from app.models.producto_category_model import ProductoCategoria
from app.models.producto_ingredient_model import ProductoIngrediente

def init_db():
    SQLModel.metadata.create_all(engine)
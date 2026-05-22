from sqlmodel import SQLModel
from app.db.database import engine

# Dominio 1 — Identidad & Acceso
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol_model import UsuarioRol
from app.models.refresh_token_model import RefreshToken
from app.models.direccion_entrega_model import DireccionEntrega

# Dominio 2 — Catálogo de Productos
from app.models.producto_model import Producto
from app.models.categoria_model import Categoria
from app.models.ingrediente_model import Ingrediente
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente

# (Dominio 3 se agregará en secciones 4-5)


def init_db():
    SQLModel.metadata.create_all(engine)
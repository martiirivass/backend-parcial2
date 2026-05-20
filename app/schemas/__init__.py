from app.schemas.producto_schema import ProductoRead, ProductoReadWithRelations
from app.schemas.categoria_schema import CategoriaRead, CategoriaReadWithProductos
from app.schemas.ingrediente_schema import IngredienteRead, IngredienteReadWithProductos

#  reconstrucción de modelos (para arreglar swagger y evitar errores de referencia circular)
#Esto permite que Pydantic resuelva tipos definidos como strings.
ProductoReadWithRelations.model_rebuild()
CategoriaReadWithProductos.model_rebuild()
IngredienteReadWithProductos.model_rebuild()
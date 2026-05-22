from app.schemas.producto_schema import ProductoRead, ProductoReadWithRelations
from app.schemas.categoria_schema import CategoriaRead, CategoriaReadWithProductos, CategoriaTree
from app.schemas.ingrediente_schema import IngredienteRead, IngredienteReadWithProductos

# Catálogos
from app.schemas.unidad_medida_schema import UnidadMedidaRead, UnidadMedidaCreate, UnidadMedidaUpdate
from app.schemas.forma_pago_schema import FormaPagoRead
from app.schemas.estado_pedido_schema import EstadoPedidoRead

# Ventas & Pagos
from app.schemas.pedido_schema import PedidoRead, PedidoReadWithDetails, PedidoCreate, DetallePedidoRead, AvanceEstadoRequest
from app.schemas.historial_estado_schema import HistorialEstadoRead
from app.schemas.pago_schema import PagoRead, PagoCreate

# Auth
from app.schemas.refresh_token_schema import RefreshTokenRead, RefreshTokenCreate

# Reconstrucción de modelos (para evitar errores de referencia circular)
ProductoReadWithRelations.model_rebuild()
CategoriaReadWithProductos.model_rebuild()
CategoriaTree.model_rebuild()
IngredienteReadWithProductos.model_rebuild()
PedidoReadWithDetails.model_rebuild()

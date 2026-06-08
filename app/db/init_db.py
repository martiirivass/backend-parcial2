from sqlmodel import SQLModel
from app.db.database import engine

# Importo todos los modelos para que SQLModel los registre
from app.models.producto_model import Producto
from app.models.categoria_model import Categoria
from app.models.ingrediente_model import Ingrediente
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente
from app.models.unidad_medida_model import UnidadMedida
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol_model import UsuarioRol
from app.models.estado_pedido_model import EstadoPedido
from app.models.forma_pago_model import FormaPago
from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.historial_estado_model import HistorialEstadoPedido
from app.models.pago_model import Pago
from app.models.direccion_entrega_model import DireccionEntrega
from app.models.refresh_token_model import RefreshToken

def init_db():
    print("[init_db] Starting...")

    SQLModel.metadata.create_all(engine)

    from app.seed import run_seed
    run_seed()

    print("[init_db] Seed OK")
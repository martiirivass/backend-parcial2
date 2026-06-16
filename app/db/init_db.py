from sqlmodel import SQLModel
from sqlalchemy import text
from app.db.database import engine

from app.models.producto_model import Producto
from app.models.categoria_model import Categoria
from app.models.ingrediente_model import Ingrediente
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente
from app.models.unidad_medida_model import UnidadMedida
from app.models.rol import Rol
from app.models.tipo_documento_model import TipoDocumento
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

    _run_migrations(engine)

    from app.db.seed import run_seed
    run_seed()

    print("[init_db] Seed OK")


def _run_migrations(engine):
    """Migraciones evolutivas: agrega columnas / renombra según el modelo actual."""
    with engine.connect() as conn:
        # ── Usuarios ──────────────────────────────────────────────────
        conn.execute(text("""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS tipo_documento_id INTEGER REFERENCES tipos_documento(id)
        """))
        conn.execute(text("""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS numero_documento VARCHAR(20)
        """))

        # ── Pagos ─────────────────────────────────────────────────────
        # La tabla 'pagos' se creó originalmente con columnas viejas
        # (referencia, created_at, updated_at). El modelo actual usa
        # (external_reference, creado_en, actualizado_en). Corregimos.

        # 1. Columnas nuevas que no existían
        conn.execute(text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS mp_payment_id BIGINT"))
        conn.execute(text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS mp_status VARCHAR(20)"))
        conn.execute(text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100)"))
        conn.execute(text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS transaction_amount FLOAT"))
        conn.execute(text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS date_approved TIMESTAMP"))

        # 2. Renombrar columnas viejas a los nombres del modelo actual
        #    (solo si la columna vieja existe y la nueva aún no)
        conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.columns
                           WHERE table_name='pagos' AND column_name='referencia')
                   AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                                   WHERE table_name='pagos' AND column_name='external_reference') THEN
                    ALTER TABLE pagos RENAME COLUMN referencia TO external_reference;
                END IF;

                IF EXISTS (SELECT 1 FROM information_schema.columns
                           WHERE table_name='pagos' AND column_name='created_at')
                   AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                                   WHERE table_name='pagos' AND column_name='creado_en') THEN
                    ALTER TABLE pagos RENAME COLUMN created_at TO creado_en;
                END IF;

                IF EXISTS (SELECT 1 FROM information_schema.columns
                           WHERE table_name='pagos' AND column_name='updated_at')
                   AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                                   WHERE table_name='pagos' AND column_name='actualizado_en') THEN
                    ALTER TABLE pagos RENAME COLUMN updated_at TO actualizado_en;
                END IF;
            END $$;
        """))

        conn.commit()
        print("[init_db] Migraciones aplicadas correctamente")

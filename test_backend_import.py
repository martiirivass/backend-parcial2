"""Simulate the EXACT backend import order"""
import sys; sys.path.insert(0, '.')
sys.argv = ['test']

# Import in the SAME order as app.main
from app.auth.router import router as auth  # noqa
from app.routers.producto_router import router as producto  # noqa
from app.routers.categoria_router import router as categoria  # noqa
from app.routers.ingrediente_router import router as ingrediente  # noqa
from app.routers.pedido_router import router as pedido  # noqa
from app.routers.direccion_router import router as direccion  # noqa
from app.routers.admin_router import router as admin  # noqa
from app.routers.stats_router import router as stats  # noqa
from app.routers.unidad_medida_router import router as unidad_medida  # noqa
from app.routers.forma_pago_router import router as forma_pago  # noqa
from app.routers.estado_pedido_router import router as estado_pedido  # noqa
from app.routers.pago_router import router as pago  # noqa
from app.routers.ws_router import router as ws  # noqa
from app.pagos.router import router as pagos  # noqa

print("[OK] All imports completed")

# Now test the REAL service call
from sqlmodel import Session
from app.db.database import engine

with Session(engine) as db:
    from app.pagos.service import PagoService
    svc = PagoService(db)
    result = svc.get_pago_status(33, 2)
    print(f"\nResult: {result}")

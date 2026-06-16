"""Simulate the SAME import chain as the real backend"""
import sys; sys.path.insert(0, '.')
sys.argv = ['test']  # Avoid config issues

# Import models in the same order the backend does
from app.models.usuario import Usuario
from app.models.detalle_pedido_model import DetallePedido
from app.models.pedido_model import Pedido
from app.models.pago_model import Pago
from sqlmodel import Session
from app.db.database import engine

# Now create a session and test the service
with Session(engine) as db:
    from app.pagos.service import PagoService
    svc = PagoService(db)
    result = svc.get_pago_status(33, 2)
    print(f"Result: {result}")

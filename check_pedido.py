import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    r = conn.execute(text('SELECT id, estado_codigo FROM pedidos WHERE id = 32')).first()
    print(f'Pedido 32: estado={r.estado_codigo}')
    r2 = conn.execute(text("SELECT id, mp_status, mp_payment_id FROM pagos WHERE pedido_id = 32")).first()
    print(f'Pago: id={r2.id} status={r2.mp_status} mp_id={r2.mp_payment_id}')

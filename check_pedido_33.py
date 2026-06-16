import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT p.id, p.estado_codigo, p.usuario_id,
               pg.id pago_id, pg.mp_status, pg.external_reference, pg.mp_payment_id
        FROM pedidos p
        LEFT JOIN pagos pg ON pg.pedido_id = p.id
        WHERE p.id = 33
    """)).all()
    if rows:
        for r in rows:
            print(f"pedido={r.id} estado={r.estado_codigo} usuario={r.usuario_id} pago_id={r.pago_id} mp_status={r.mp_status} ext_ref={r.external_reference} mp_id={r.mp_payment_id}")
    else:
        print("No pedido 33 found")

    # Also check if there are any pagos without a matching pedido
    orphans = conn.execute(text("""
        SELECT pg.id FROM pagos pg LEFT JOIN pedidos p ON p.id = pg.pedido_id WHERE p.id IS NULL
    """)).all()
    if orphans:
        print(f"Orphan pagos: {[o.id for o in orphans]}")

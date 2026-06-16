import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT p.id pedido, p.estado_codigo, 
               pg.id pago_id, pg.mp_status, pg.external_reference, pg.mp_payment_id
        FROM pedidos p
        LEFT JOIN pagos pg ON pg.pedido_id = p.id
        ORDER BY p.id DESC
        LIMIT 15
    """)).all()
    print(f"{'pedido':>6} {'estado':<15} {'pago_id':>7} {'mp_status':<12} {'ext_ref':<15} {'mp_payment_id':<18}")
    print("-"*80)
    for r in rows:
        print(f"{r.pedido:>6} {r.estado_codigo:<15} {str(r.pago_id or '-'):>7} {str(r.mp_status or '-'):<12} {str(r.external_reference or '-'):<15} {str(r.mp_payment_id or '-'):<18}")

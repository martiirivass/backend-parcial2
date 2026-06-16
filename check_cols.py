import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
cols = inspector.get_columns('pagos')
for c in cols:
    if c['name'] in ('mp_payment_id', 'id', 'transaction_amount'):
        print(f"{c['name']}: {c['type']}")

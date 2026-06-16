import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    rows = conn.execute(text("SELECT id, email, nombre FROM usuarios WHERE id IN (1, 2, 3)")).all()
    for r in rows:
        print(f"id={r.id} email={r.email} nombre={r.nombre}")

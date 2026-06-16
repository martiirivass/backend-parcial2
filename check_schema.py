import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    rows = conn.execute(text("SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = 'pagos' ORDER BY ordinal_position")).fetchall()
    for r in rows:
        extra = f"({r.character_maximum_length})" if r.character_maximum_length else ""
        print(f"{r.column_name:25s} {r.data_type}{extra}")

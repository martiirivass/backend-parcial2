import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text, inspect
with engine.connect() as conn:
    # Check actual table names
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    print("Tables in DB:")
    for t in tables:
        print(f"  {t}")
    
    # Check usuarios directly
    print("\n--- usuarios ---")
    rows = conn.execute(text("SELECT id, email, nombre FROM usuarios")).all()
    for r in rows:
        print(f"  id={r.id} email={r.email} nombre={r.nombre}")
    
    # Check if there's a roles table
    if "roles" in tables:
        print("\n--- roles ---")
        rows = conn.execute(text("SELECT * FROM roles")).all()
        for r in rows:
            print(f"  id={r.id} codigo={r.codigo} nombre={r.nombre}")

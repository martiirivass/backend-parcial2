import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    # Check roles
    rows = conn.execute(text("SELECT * FROM roles")).all()
    cols = rows[0]._mapping.keys() if rows else []
    print(f"Roles columns: {list(cols)}")
    for r in rows:
        vals = dict(r._mapping)
        print(f"  {vals}")
    
    # Check usuario_rol
    rows2 = conn.execute(text("SELECT * FROM usuario_rol")).all()
    cols2 = rows2[0]._mapping.keys() if rows2 else []
    print(f"\nUsuario_Rol columns: {list(cols2)}")
    for r in rows2:
        vals = dict(r._mapping)
        print(f"  {vals}")

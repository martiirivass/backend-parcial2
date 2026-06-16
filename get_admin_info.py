import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT u.id, u.email, u.nombre, u.password_hash,
               r.codigo as rol_codigo
        FROM usuarios u
        JOIN usuario_roles ur ON ur.usuario_id = u.id
        JOIN roles r ON r.id = ur.rol_id
        WHERE r.codigo LIKE '%ADMIN%'
        ORDER BY u.id
    """)).all()
    for r in rows:
        print(f"id={r.id} email={r.email} nombre={r.nombre} rol={r.rol_codigo} hash={r.password_hash[:30]}...")
    
    print("\n--- All roles ---")
    roles = conn.execute(text("SELECT id, codigo, nombre FROM roles")).all()
    for role in roles:
        print(f"  id={role.id} codigo={role.codigo} nombre={role.nombre}")

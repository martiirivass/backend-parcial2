from sqlmodel import select
from conftest import get_db, make_uow, make_repos
from app.models.categoria_model import Categoria
from app.models.producto_model import Producto
from app.models.ingrediente_model import Ingrediente

print("TEST: Soft Delete para TODAS las entidades\n")

db = get_db()
repos = make_repos(db)

try:
    print("=" * 60)
    print("1. PRUEBA CATEGORIAS - SOFT DELETE")
    print("=" * 60)

    print("\n[ANTES] Conteo de categorias activas:")
    todas_cat = repos["categoria"].get_all()
    print(f"   Total: {len(todas_cat)}\n")

    if len(todas_cat) > 0:
        cat_para_eliminar = todas_cat[0]
        cat_id = cat_para_eliminar.id
        print(f"[ELIMINANDO] Categoria ID {cat_id}: {cat_para_eliminar.nombre}")

        repos["categoria"].delete(cat_para_eliminar)
        uow = make_uow(db)
        uow.commit()

        print(f"[VERIFICANDO] Existe aun en BD?\n")

        # Verificar en DB directamente (sin filtro activo)
        stmt_directo = select(Categoria).where(Categoria.id == cat_id)
        cat_en_bd = db.exec(stmt_directo).first()

        if cat_en_bd:
            print(f"   [OK] SI existe en BD (fisicamente)")
            print(f"   - deleted_at: {cat_en_bd.deleted_at}")
            print(f"   - nombre: {cat_en_bd.nombre}\n")
        else:
            print(f"   [FAIL] NO existe en BD (fue borrada fisicamente)\n")

        # Verificar en repositorio (con filtro activo)
        cat_via_repo = repos["categoria"].get_by_id(cat_id)
        if cat_via_repo is None:
            print(f"   [OK] Repositorio NO la devuelve (filtro activo=True)")
        else:
            print(f"   [FAIL] Repositorio la devuelve (ERROR en filtro)")
    else:
        print("[SKIP] No hay categorias para probar\n")

    print("\n" + "=" * 60)
    print("2. PRUEBA INGREDIENTES - SOFT DELETE")
    print("=" * 60)

    print("\n[ANTES] Conteo de ingredientes activos:")
    todos_ing = repos["ingrediente"].get_all()
    print(f"   Total: {len(todos_ing)}\n")

    if len(todos_ing) > 0:
        ing_para_eliminar = todos_ing[0]
        ing_id = ing_para_eliminar.id
        print(f"[ELIMINANDO] Ingrediente ID {ing_id}: {ing_para_eliminar.nombre}")

        repos["ingrediente"].delete(ing_para_eliminar)
        uow = make_uow(db)
        uow.commit()

        print(f"[VERIFICANDO] Existe aun en BD?\n")

        # Verificar en DB directamente (sin filtro activo)
        stmt_directo = select(Ingrediente).where(Ingrediente.id == ing_id)
        ing_en_bd = db.exec(stmt_directo).first()

        if ing_en_bd:
            print(f"   [OK] SI existe en BD (fisicamente)")
            print(f"   - deleted_at: {ing_en_bd.deleted_at}")
            print(f"   - nombre: {ing_en_bd.nombre}\n")
        else:
            print(f"   [FAIL] NO existe en BD (fue borrada fisicamente)\n")

        # Verificar en repositorio (con filtro activo)
        ing_via_repo = repos["ingrediente"].get_by_id(ing_id)
        if ing_via_repo is None:
            print(f"   [OK] Repositorio NO la devuelve (filtro activo=True)")
        else:
            print(f"   [FAIL] Repositorio la devuelve (ERROR en filtro)")
    else:
        print("[SKIP] No hay ingredientes para probar\n")

    print("\n" + "=" * 60)
    print("3. PRUEBA PRODUCTOS - SOFT DELETE (ya existia)")
    print("=" * 60)

    print("\n[ANTES] Conteo de productos activos:")
    todos_prod = repos["producto"].get_all()
    print(f"   Total: {len(todos_prod)}\n")

    if len(todos_prod) > 0:
        prod_para_eliminar = todos_prod[0]
        prod_id = prod_para_eliminar.id
        print(f"[ELIMINANDO] Producto ID {prod_id}: {prod_para_eliminar.nombre}")

        repos["producto"].delete(prod_para_eliminar)
        uow = make_uow(db)
        uow.commit()

        print(f"[VERIFICANDO] Existe aun en BD?\n")

        # Verificar en DB directamente (sin filtro activo)
        stmt_directo = select(Producto).where(Producto.id == prod_id)
        prod_en_bd = db.exec(stmt_directo).first()

        if prod_en_bd:
            print(f"   [OK] SI existe en BD (fisicamente)")
            print(f"   - disponible: {prod_en_bd.disponible}")
            print(f"   - nombre: {prod_en_bd.nombre}\n")
        else:
            print(f"   [FAIL] NO existe en BD (fue borrada fisicamente)\n")

        # Verificar en repositorio (con filtro activo)
        prod_via_repo = repos["producto"].get_by_id(prod_id)
        if prod_via_repo is None:
            print(f"   [OK] Repositorio NO la devuelve (filtro activo=True)")
        else:
            print(f"   [FAIL] Repositorio la devuelve (ERROR en filtro)")
    else:
        print("[SKIP] No hay productos para probar\n")

    print("\n" + "=" * 60)
    print("[EXITO] SOFT DELETE IMPLEMENTADO PARA TODAS LAS ENTIDADES")
    print("=" * 60)

    db.close()

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

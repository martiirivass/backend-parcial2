from conftest import get_db, make_uow, make_repos
from app.models.producto_model import Producto
from app.schemas.producto_schema import ProductoCreate

print("TEST: Productos (GET, POST)\n")

try:
    db = get_db()
    repos = make_repos(db)

    print("[1] GET /productos...")
    productos = repos["producto"].get_all()
    print(f"    [OK] {len(productos)} productos en BD\n")

    print("[2] GET /categorias...")
    categorias = repos["categoria"].get_all()
    print(f"    [OK] {len(categorias)} categorías en BD\n")

    print("[2b] GET /ingredientes...")
    ingredientes = repos["ingrediente"].get_all()
    print(f"    [OK] {len(ingredientes)} ingredientes en BD\n")

    if len(categorias) == 0 or len(ingredientes) == 0:
        print("[SKIP] No hay categorías o ingredientes para crear producto")
    else:
        print("[3] POST /productos...")
        prod_create = ProductoCreate(
            nombre="ProductoTest",
            descripcion="Test description",
            precio_base=99.99,
            categoria_ids=[categorias[0].id],
            ingrediente_ids=[ingredientes[0].id]
        )
        print(f"    Schema: {prod_create}\n")

        nuevo = Producto(
            nombre=prod_create.nombre,
            descripcion=prod_create.descripcion,
            precio_base=prod_create.precio_base
        )
        print(f"    [OK] Modelo creado\n")

        print("[4] Asignando categorías...")
        if prod_create.categoria_ids:
            nuevas_cats = [repos["categoria"].get_by_id(cid) for cid in prod_create.categoria_ids]
            nuevo.categorias = [c for c in nuevas_cats if c]
            print(f"    [OK] {len(nuevo.categorias)} categorías asignadas\n")

        print("[5] Guardando producto...")
        repos["producto"].create(nuevo)
        uow = make_uow(db)
        uow.commit()
        db.refresh(nuevo)
        print(f"    [OK] Producto ID: {nuevo.id}\n")

        print(f"[EXITO] Producto creado: {nuevo.nombre}")

    db.close()

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

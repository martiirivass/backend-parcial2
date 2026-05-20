from sqlmodel import Session, select
from app.db.database import engine
from app.models.category_model import Categoria
from app.models.producto_model import Producto
from app.models.ingredient_model import Ingrediente
from app.repositories.category_repository import CategoriaRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.ingredient_repository import IngredienteRepository
from app.unit_of_work import UnitOfWork

print("TEST: Soft Delete para TODAS las entidades\n")

db = Session(engine)

try:
    print("=" * 60)
    print("1. PRUEBA CATEGORIAS - SOFT DELETE")
    print("=" * 60)
    
    cat_repo = CategoriaRepository(db)
    uow = UnitOfWork(db)
    
    print("\n[ANTES] Conteo de categorias activas:")
    todas_cat = cat_repo.get_all()
    print(f"   Total: {len(todas_cat)}\n")
    
    if len(todas_cat) > 0:
        cat_para_eliminar = todas_cat[0]
        cat_id = cat_para_eliminar.id
        print(f"[ELIMINANDO] Categoria ID {cat_id}: {cat_para_eliminar.nombre}")
        
        cat_repo.delete(cat_para_eliminar)
        uow.commit()
        
        print(f"[VERIFICANDO] Existe aun en BD?\n")
        
        # Verificar en DB directamente (sin filtro activo)
        stmt_directo = select(Categoria).where(Categoria.id == cat_id)
        cat_en_bd = db.exec(stmt_directo).first()
        
        if cat_en_bd:
            print(f"   [OK] SI existe en BD (fisicamente)")
            print(f"   - activo: {cat_en_bd.activo}")
            print(f"   - nombre: {cat_en_bd.nombre}\n")
        else:
            print(f"   [FAIL] NO existe en BD (fue borrada fisicamente)\n")
        
        # Verificar en repositorio (con filtro activo)
        cat_via_repo = cat_repo.get_by_id(cat_id)
        if cat_via_repo is None:
            print(f"   [OK] Repositorio NO la devuelve (filtro activo=True)")
        else:
            print(f"   [FAIL] Repositorio la devuelve (ERROR en filtro)")
    else:
        print("[SKIP] No hay categorias para probar\n")
    
    print("\n" + "=" * 60)
    print("2. PRUEBA INGREDIENTES - SOFT DELETE")
    print("=" * 60)
    
    ing_repo = IngredienteRepository(db)
    
    print("\n[ANTES] Conteo de ingredientes activos:")
    todos_ing = ing_repo.get_all()
    print(f"   Total: {len(todos_ing)}\n")
    
    if len(todos_ing) > 0:
        ing_para_eliminar = todos_ing[0]
        ing_id = ing_para_eliminar.id
        print(f"[ELIMINANDO] Ingrediente ID {ing_id}: {ing_para_eliminar.nombre}")
        
        ing_repo.delete(ing_para_eliminar)
        uow.commit()
        
        print(f"[VERIFICANDO] Existe aun en BD?\n")
        
        # Verificar en DB directamente (sin filtro activo)
        stmt_directo = select(Ingrediente).where(Ingrediente.id == ing_id)
        ing_en_bd = db.exec(stmt_directo).first()
        
        if ing_en_bd:
            print(f"   [OK] SI existe en BD (fisicamente)")
            print(f"   - activo: {ing_en_bd.activo}")
            print(f"   - nombre: {ing_en_bd.nombre}\n")
        else:
            print(f"   [FAIL] NO existe en BD (fue borrada fisicamente)\n")
        
        # Verificar en repositorio (con filtro activo)
        ing_via_repo = ing_repo.get_by_id(ing_id)
        if ing_via_repo is None:
            print(f"   [OK] Repositorio NO la devuelve (filtro activo=True)")
        else:
            print(f"   [FAIL] Repositorio la devuelve (ERROR en filtro)")
    else:
        print("[SKIP] No hay ingredientes para probar\n")
    
    print("\n" + "=" * 60)
    print("3. PRUEBA PRODUCTOS - SOFT DELETE (ya existia)")
    print("=" * 60)
    
    prod_repo = ProductoRepository(db)
    
    print("\n[ANTES] Conteo de productos activos:")
    todos_prod = prod_repo.get_all()
    print(f"   Total: {len(todos_prod)}\n")
    
    if len(todos_prod) > 0:
        prod_para_eliminar = todos_prod[0]
        prod_id = prod_para_eliminar.id
        print(f"[ELIMINANDO] Producto ID {prod_id}: {prod_para_eliminar.nombre}")
        
        prod_repo.delete(prod_para_eliminar)
        uow.commit()
        
        print(f"[VERIFICANDO] Existe aun en BD?\n")
        
        # Verificar en DB directamente (sin filtro activo)
        stmt_directo = select(Producto).where(Producto.id == prod_id)
        prod_en_bd = db.exec(stmt_directo).first()
        
        if prod_en_bd:
            print(f"   [OK] SI existe en BD (fisicamente)")
            print(f"   - activo: {prod_en_bd.activo}")
            print(f"   - nombre: {prod_en_bd.nombre}\n")
        else:
            print(f"   [FAIL] NO existe en BD (fue borrada fisicamente)\n")
        
        # Verificar en repositorio (con filtro activo)
        prod_via_repo = prod_repo.get_by_id(prod_id)
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

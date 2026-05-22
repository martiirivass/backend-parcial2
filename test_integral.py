"""
Test integral del backend.
Requiere que el seed se haya ejecutado (init_db corrió al menos una vez).
Correr con: python test_integral.py
"""
from sqlmodel import Session, select
from app.db.database import engine
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.unidad_medida_model import UnidadMedida
from app.models.forma_pago_model import FormaPago
from app.models.estado_pedido_model import EstadoPedido
from app.models.categoria_model import Categoria
from app.models.ingrediente_model import Ingrediente
from app.models.producto_model import Producto
from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.historial_estado_model import HistorialEstadoPedido
from app.models.pago_model import Pago
from app.models.refresh_token_model import RefreshToken
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.pedido_repository import PedidoRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.unit_of_work import UnitOfWork
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.services import register_user
from datetime import datetime, timezone

ok = 0
fail = 0


def check(nombre, condicion, detalle=""):
    global ok, fail
    if condicion:
        ok += 1
        print(f"  ✅ {nombre}")
    else:
        fail += 1
        print(f"  ❌ {nombre} — {detalle}")


print("=" * 60)
print("TEST INTEGRAL — BACKEND PARCIAL 2")
print("=" * 60)

db = Session(engine)

try:
    # ============================================================
    print("\n📦 1. SEED DATA — Catalogos basicos")
    # ============================================================
    roles = db.exec(select(Rol)).all()
    check("Roles creados", len(roles) >= 4, f"Tiene {len(roles)}")

    unidades = db.exec(select(UnidadMedida)).all()
    check("Unidades de medida creadas", len(unidades) >= 5, f"Tiene {len(unidades)}")

    estados = db.exec(select(EstadoPedido)).all()
    check("Estados de pedido creados", len(estados) >= 6, f"Tiene {len(estados)}")

    formas = db.exec(select(FormaPago)).all()
    check("Formas de pago creadas", len(formas) >= 3, f"Tiene {len(formas)}")

    # ============================================================
    print("\n📦 2. SEED DATA — Admin y demo")
    # ============================================================
    admin = db.exec(select(Usuario).where(Usuario.email == "admin@admin.com")).first()
    check("Admin creado", admin is not None)
    if admin:
        check("Admin tiene roles", len(admin.roles) > 0, f"Roles: {[r.codigo for r in admin.roles]}")
        check("Admin es ADMIN", admin.tiene_rol("ADMIN"))

    categorias = db.exec(select(Categoria)).all()
    check("Categorias de ejemplo creadas", len(categorias) >= 5, f"Tiene {len(categorias)}")

    ingredientes = db.exec(select(Ingrediente)).all()
    check("Ingredientes de ejemplo creados", len(ingredientes) >= 10, f"Tiene {len(ingredientes)}")

    productos = db.exec(select(Producto)).all()
    check("Productos de ejemplo creados", len(productos) >= 4, f"Tiene {len(productos)}")

    # ============================================================
    print("\n📦 3. SOFT DELETE")
    # ============================================================
    cat_repo = CategoriaRepository(db)
    todas_cat = cat_repo.get_all()
    if len(todas_cat) > 0:
        cat_para_borrar = todas_cat[0]
        cat_id = cat_para_borrar.id
        cat_repo.delete(cat_para_borrar)
        db.commit()

        # Verifico que no aparezca en get_all
        despues = cat_repo.get_all()
        check("Soft delete: categoria no aparece en get_all()", cat_id not in [c.id for c in despues])

        # Verifico que el deleted_at tenga fecha
        cat_db = db.get(Categoria, cat_id)
        check("Soft delete: deleted_at tiene fecha", cat_db.deleted_at is not None)

        # Restauro para no romper tests siguientes
        cat_db.deleted_at = None
        db.add(cat_db)
        db.commit()

    # ============================================================
    print("\n📦 4. USUARIOS — Register y Password")
    # ============================================================
    check("Hash password funciona", verify_password("admin123", admin.password) if admin else False)
    check("Hash password rechaza incorrecta", not verify_password("wrong", admin.password) if admin else False)

    # ============================================================
    print("\n📦 5. REPOSITORIOS — CRUD basico")
    # ============================================================
    prod_repo = ProductoRepository(db)
    todos_prod = prod_repo.get_all()
    check("ProductoRepository.get_all()", len(todos_prod) > 0, f"Tiene {len(todos_prod)}")

    if len(todos_prod) > 0:
        un_producto = prod_repo.get_by_id(todos_prod[0].id)
        check("ProductoRepository.get_by_id()", un_producto is not None)

    pedido_repo = PedidoRepository(db)
    todos_ped = pedido_repo.get_all()
    check("PedidoRepository.get_all() (vacio ok)", isinstance(todos_ped, list))

    # ============================================================
    print("\n📦 6. PEDIDOS — Creacion y workflow")
    # ============================================================
    from app.services.pedido_service import PedidoService
    from app.schemas.pedido_schema import PedidoCreate, DetallePedidoCreate

    ps = PedidoService(db)

    # Busco un CLIENT para crear pedido
    # Creo un usuario de prueba si no existe
    cliente = db.exec(select(Usuario).where(Usuario.email == "test@test.com")).first()
    if not cliente:
        uow = UnitOfWork(db)
        try:
            cliente = register_user(
                nombre="Test",
                email="test@test.com",
                password="test123",
                session=db
            )
            # Le asigno rol CLIENT
            from app.models.usuario_rol_model import UsuarioRol
            rol_cliente = db.exec(select(Rol).where(Rol.codigo == "CLIENT")).first()
            if rol_cliente:
                ur = UsuarioRol(usuario_id=cliente.id, rol_codigo=rol_cliente.codigo)
                db.add(ur)
            uow.commit()
            db.refresh(cliente)
        except Exception:
            uow.rollback()
            cliente = None

    check("Usuario CLIENT creado para tests", cliente is not None)

    if cliente and len(productos) > 0:
        # Creo pedido
        try:
            uow2 = UnitOfWork(db)
            pedido_creado = ps.crear_pedido(cliente.id, PedidoCreate(
                forma_pago_codigo="EFECTIVO",
                items=[DetallePedidoCreate(producto_id=productos[0].id, cantidad=2)]
            ))
            check("Pedido creado exitosamente", pedido_creado is not None)
            check("Pedido tiene estado PENDIENTE", pedido_creado.estado_codigo == "PENDIENTE")
            check("Pedido calculo total correcto", pedido_creado.total > 0)
            check("Pedido tiene subtotal", pedido_creado.subtotal > 0)
            check("Pedido tiene costo_envio", pedido_creado.costo_envio > 0)

            # Verifico detalle
            detalles = db.exec(
                select(DetallePedido).where(DetallePedido.pedido_id == pedido_creado.id)
            ).all()
            check("DetallePedido creado", len(detalles) >= 1)
            if len(detalles) > 0:
                d = detalles[0]
                check("Snapshot: nombre_snapshot guardado", d.nombre_snapshot == productos[0].nombre)
                check("Snapshot: precio_snapshot guardado", d.precio_snapshot == productos[0].precio)
                check("Snapshot: subtotal_snap calculado", d.subtotal_snap > 0)
                check("Snapshot: cantidad correcta", d.cantidad == 2)

            # Verifico historial
            historial = db.exec(
                select(HistorialEstadoPedido)
                .where(HistorialEstadoPedido.pedido_id == pedido_creado.id)
            ).all()
            check("HistorialEstado creado (PENDIENTE)", len(historial) >= 1)
            if len(historial) > 0:
                check("Historial: estado_codigo correcto", historial[0].estado_codigo == "PENDIENTE")

            # Avanzo estado
            pedido_avanzado = ps.avanzar_estado(pedido_creado.id, "CONFIRMADO")
            pedido_avanzado2 = ps.avanzar_estado(pedido_creado.id, "EN_PREP")
            pedido_avanzado3 = ps.avanzar_estado(pedido_creado.id, "EN_CAMINO")
            check("Estado avanzado a EN_CAMINO", pedido_avanzado3.estado_codigo == "EN_CAMINO")

            # Verifico historial actualizado
            historial2 = db.exec(
                select(HistorialEstadoPedido)
                .where(HistorialEstadoPedido.pedido_id == pedido_creado.id)
                .order_by(HistorialEstadoPedido.fecha)
            ).all()
            check("Historial: 4 entradas (PEND+CONF+EN_PREP+EN_CAMINO)", len(historial2) == 4)

            # Transicion invalida (ENTREGADO -> CANCELADO no es valida pero EN_CAMINO -> ENTREGADO si)
            pedido_entregado = ps.avanzar_estado(pedido_creado.id, "ENTREGADO")
            check("Estado avanzado a ENTREGADO", pedido_entregado.estado_codigo == "ENTREGADO")

            # Intento transicion invalida
            try:
                ps.avanzar_estado(pedido_creado.id, "CANCELADO")
                check("Transicion invalida ENTREGADO->CANCELADO RECHAZADA", False, "Deberia haber lanzado excepcion")
            except Exception:
                check("Transicion invalida ENTREGADO->CANCELADO RECHAZADA", True)

        except Exception as e:
            uow2.rollback()
            check(f"Error en test de pedidos: {e}", False, str(e))

    # ============================================================
    print("\n📦 7. PAGOS — Registro")
    # ============================================================
    if cliente and len(productos) > 0:
        from app.services.pago_service import PagoService
        from app.schemas.pago_schema import PagoCreate

        pago_svc = PagoService(db)
        try:
            uow3 = UnitOfWork(db)
            # Creo un pedido nuevo para pagar
            pedido_pago = ps.crear_pedido(cliente.id, PedidoCreate(
                forma_pago_codigo="EFECTIVO",
                items=[DetallePedidoCreate(producto_id=productos[0].id, cantidad=1)]
            ))

            pago = pago_svc.registrar_pago(PagoCreate(
                pedido_id=pedido_pago.id,
                monto=pedido_pago.total,
                forma_pago_codigo="EFECTIVO"
            ))
            check("Pago registrado exitosamente", pago is not None)
            check("Pago monto correcto", pago.monto == pedido_pago.total)
            check("Pago forma_pago_codigo correcto", pago.forma_pago_codigo == "EFECTIVO")
            check("Pago tiene referencia nullable", pago.referencia is None)

            # Pago duplicado deberia fallar (excede saldo)
            try:
                pago_svc.registrar_pago(PagoCreate(
                    pedido_id=pedido_pago.id,
                    monto=1.0,
                    forma_pago_codigo="EFECTIVO"
                ))
                check("Pago excede saldo RECHAZADO", False, "Deberia haber lanzado excepcion")
            except Exception:
                check("Pago excede saldo RECHAZADO", True)

        except Exception as e:
            uow3.rollback()
            check(f"Error en test de pagos: {e}", False, str(e))

    # ============================================================
    print("\n📦 8. REFRESH TOKENS")
    # ============================================================
    repo_rt = RefreshTokenRepository(db)
    if admin:
        # Creo un refresh token manualmente
        import secrets
        from datetime import timedelta

        rt = RefreshToken(
            usuario_id=admin.id,
            token=secrets.token_urlsafe(64),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(rt)
        db.commit()

        valido = repo_rt.get_valid_token(rt.token)
        check("RefreshTokenRepository: token valido encontrado", valido is not None)
        check("RefreshTokenRepository: token pertenece al admin", valido.usuario_id == admin.id if valido else False)

        # Revoco
        repo_rt.revoke_user_tokens(admin.id)
        db.commit()
        invalido = repo_rt.get_valid_token(rt.token)
        check("RefreshTokenRepository: token revocado no es valido", invalido is None)

    # ============================================================
    print("\n📦 9. PRODUCTOS — Nuevos campos")
    # ============================================================
    if len(productos) > 0:
        p = productos[0]
        check("Producto tiene stock_cantidad", hasattr(p, "stock_cantidad"))
        check("Producto tiene disponible", hasattr(p, "disponible"))
        check("Producto tiene imagen_url", hasattr(p, "imagen_url"))
        check("Producto tiene created_at", hasattr(p, "created_at") and p.created_at is not None)
        check("Producto tiene updated_at", hasattr(p, "updated_at") and p.updated_at is not None)
        check("Producto tiene deleted_at (nullable)", hasattr(p, "deleted_at") and p.deleted_at is None)

    # ============================================================
    print("\n📦 10. CATEGORIAS — Nuevos campos")
    # ============================================================
    if len(categorias) > 0:
        c = categorias[0]
        check("Categoria tiene created_at", hasattr(c, "created_at") and c.created_at is not None)
        check("Categoria tiene updated_at", hasattr(c, "updated_at") and c.updated_at is not None)
        check("Categoria tiene deleted_at (nullable)", hasattr(c, "deleted_at") and c.deleted_at is None)

except Exception as e:
    import traceback
    print(f"\n💥 ERROR FATAL: {e}")
    traceback.print_exc()
    fail += 1

finally:
    db.close()

# ============================================================
print(f"\n{'=' * 60}")
print(f"RESULTADOS: {ok} pasaron ✅ | {fail} fallaron ❌")
print(f"{'=' * 60}")

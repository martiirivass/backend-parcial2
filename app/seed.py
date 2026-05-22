from sqlmodel import Session, select
from app.db.database import engine
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.estado_pedido_model import EstadoPedido
from app.models.forma_pago_model import FormaPago
from app.models.unidad_medida_model import UnidadMedida
from app.models.categoria_model import Categoria
from app.models.ingrediente_model import Ingrediente
from app.models.producto_model import Producto
from app.models.producto_categoria_model import ProductoCategoria
from app.models.producto_ingrediente_model import ProductoIngrediente
from app.auth.security import hash_password


def run_seed():
    with Session(engine) as session:
        seed_roles(session)
        seed_unidades_medida(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
        seed_admin(session)
        seed_categorias_ingredientes(session)
        seed_productos_ejemplo(session)
        session.commit()
        print("Seed ejecutado correctamente")


def seed_roles(session):
    roles_data = [
        {"codigo": "ADMIN", "nombre": "Administrador"},
        {"codigo": "STOCK", "nombre": "Gestor de Stock"},
        {"codigo": "PEDIDOS", "nombre": "Gestor de Pedidos"},
        {"codigo": "CLIENT", "nombre": "Cliente"},
    ]

    for r in roles_data:
        existe = session.exec(
            select(Rol).where(Rol.codigo == r["codigo"])
        ).first()
        if not existe:
            session.add(Rol(**r))
            print(f"  Rol creado: {r['codigo']}")
        else:
            print(f"  Rol ya existe: {r['codigo']}")


def seed_unidades_medida(session):
    unidades_data = [
        {"nombre": "Kilogramo", "simbolo": "kg", "tipo": "masa"},
        {"nombre": "Gramo", "simbolo": "g", "tipo": "masa"},
        {"nombre": "Litro", "simbolo": "L", "tipo": "volumen"},
        {"nombre": "Mililitro", "simbolo": "mL", "tipo": "volumen"},
        {"nombre": "Unidad", "simbolo": "u", "tipo": "unidad"},
        {"nombre": "Docena", "simbolo": "doc", "tipo": "unidad"},
        {"nombre": "Metro cuadrado", "simbolo": "m²", "tipo": "area"},
    ]

    for u in unidades_data:
        existe = session.exec(
            select(UnidadMedida).where(UnidadMedida.nombre == u["nombre"])
        ).first()
        if not existe:
            session.add(UnidadMedida(**u))
            print(f"  Unidad creada: {u['nombre']} ({u['simbolo']})")
        else:
            print(f"  Unidad ya existe: {u['nombre']}")


def seed_estados_pedido(session):
    estados_data = [
        {"codigo": "PENDIENTE", "descripcion": "Pedido creado, esperando confirmacion", "orden": 1, "es_terminal": False},
        {"codigo": "CONFIRMADO", "descripcion": "Pedido confirmado, en proceso de preparacion", "orden": 2, "es_terminal": False},
        {"codigo": "EN_PREP", "descripcion": "Pedido siendo preparado", "orden": 3, "es_terminal": False},
        {"codigo": "EN_CAMINO", "descripcion": "Pedido en camino al destino", "orden": 4, "es_terminal": False},
        {"codigo": "ENTREGADO", "descripcion": "Pedido entregado al cliente", "orden": 5, "es_terminal": True},
        {"codigo": "CANCELADO", "descripcion": "Pedido cancelado", "orden": 6, "es_terminal": True},
    ]

    for e in estados_data:
        existe = session.exec(
            select(EstadoPedido).where(EstadoPedido.codigo == e["codigo"])
        ).first()
        if not existe:
            session.add(EstadoPedido(**e))
            print(f"  Estado creado: {e['codigo']}")
        else:
            print(f"  Estado ya existe: {e['codigo']}")


def seed_formas_pago(session):
    formas_data = [
        {"codigo": "EFECTIVO", "descripcion": "Pago en efectivo al recibir", "habilitado": True},
        {"codigo": "TARJETA", "descripcion": "Debito o credito", "habilitado": True},
        {"codigo": "TRANSFERENCIA", "descripcion": "Transferencia bancaria", "habilitado": True},
    ]

    for f in formas_data:
        existe = session.exec(
            select(FormaPago).where(FormaPago.codigo == f["codigo"])
        ).first()
        if not existe:
            session.add(FormaPago(**f))
            print(f"  Forma de pago creada: {f['codigo']}")
        else:
            print(f"  Forma de pago ya existe: {f['codigo']}")


def seed_admin(session):
    # Busco el rol ADMIN
    rol_admin = session.exec(
        select(Rol).where(Rol.codigo == "ADMIN")
    ).first()

    if not rol_admin:
        print("  ERROR: No se encontro el rol ADMIN, ejecutar seed_roles primero")
        return

    # Me fijo si ya existe el admin
    admin = session.exec(
        select(Usuario).where(Usuario.email == "admin@admin.com")
    ).first()

    if not admin:
        admin = Usuario(
            nombre="Admin",
            apellido="Sistema",
            email="admin@admin.com",
            password_hash=hash_password("admin123"),
        )
        session.add(admin)
        session.flush()

        # Asigno el rol ADMIN via UsuarioRol (N:N)
        from app.models.usuario_rol_model import UsuarioRol
        ur = UsuarioRol(usuario_id=admin.id, rol_codigo=rol_admin.codigo)
        session.add(ur)

        print("  Usuario admin creado: admin@admin.com / admin123")
    else:
        print("  Usuario admin ya existe")


def seed_categorias_ingredientes(session):
    categorias_data = [
        {"nombre": "Hamburguesas", "descripcion": "Hamburguesas clasicas y especiales"},
        {"nombre": "Pizzas", "descripcion": "Pizzas artesanales"},
        {"nombre": "Bebidas", "descripcion": "Gaseosas, jugos y aguas"},
        {"nombre": "Postres", "descripcion": "Dulces y postres caseros"},
        {"nombre": "Papas y Acompanantes", "descripcion": "Papas fritas, aros de cebolla, etc."},
        {"nombre": "Ensaladas", "descripcion": "Ensaladas frescas"},
        {"nombre": "Parrilla", "descripcion": "Carnes a la parrilla"},
    ]

    categorias = {}
    for c in categorias_data:
        existe = session.exec(
            select(Categoria).where(Categoria.nombre == c["nombre"])
        ).first()
        if not existe:
            nueva = Categoria(**c)
            session.add(nueva)
            session.flush()
            categorias[c["nombre"]] = nueva
            print(f"  Categoria creada: {c['nombre']}")
        else:
            categorias[c["nombre"]] = existe
            print(f"  Categoria ya existe: {c['nombre']}")

    ingredientes_data = [
        {"nombre": "Carne de res", "descripcion": "Carne molida de res 200g", "es_alergeno": False},
        {"nombre": "Pan de hamburguesa", "descripcion": "Pan artesanal con sesamo", "es_alergeno": False},
        {"nombre": "Queso cheddar", "descripcion": "Queso cheddar en fetas", "es_alergeno": True},
        {"nombre": "Lechuga", "descripcion": "Lechuga criolla fresca", "es_alergeno": False},
        {"nombre": "Tomate", "descripcion": "Tomate redondo fresco", "es_alergeno": False},
        {"nombre": "Cebolla", "descripcion": "Cebolla morada", "es_alergeno": False},
        {"nombre": "Panceta", "descripcion": "Panceta ahumada crocante", "es_alergeno": False},
        {"nombre": "Huevo", "descripcion": "Huevo fresco de granja", "es_alergeno": True},
        {"nombre": "Masa de pizza", "descripcion": "Masa madre artesanal", "es_alergeno": False},
        {"nombre": "Salsa de tomate", "descripcion": "Salsa de tomates naturales", "es_alergeno": False},
        {"nombre": "Mozzarella", "descripcion": "Queso mozzarella fresco", "es_alergeno": True},
        {"nombre": "Pepperoni", "descripcion": "Salame tipo pepperoni", "es_alergeno": False},
        {"nombre": "Papa", "descripcion": "Papa blanca", "es_alergeno": False},
        {"nombre": "Aceite", "descripcion": "Aceite vegetal", "es_alergeno": False},
        {"nombre": "Pechuga de pollo", "descripcion": "Pechuga de pollo deshuesada", "es_alergeno": False},
    ]

    for i in ingredientes_data:
        existe = session.exec(
            select(Ingrediente).where(Ingrediente.nombre == i["nombre"])
        ).first()
        if not existe:
            session.add(Ingrediente(**i))
            print(f"  Ingrediente creado: {i['nombre']}")
        else:
            print(f"  Ingrediente ya existe: {i['nombre']}")

    return categorias


def seed_productos_ejemplo(session):
    # Busco unidades de medida
    kg = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "kg")).first()
    g = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "g")).first()
    L = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "L")).first()
    mL = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "mL")).first()
    unid = session.exec(select(UnidadMedida).where(UnidadMedida.simbolo == "u")).first()

    # Busco ingredientes por nombre
    ing = {}
    for nombre in ["Carne de res", "Pan de hamburguesa", "Queso cheddar", "Lechuga", "Tomate",
                    "Cebolla", "Panceta", "Huevo", "Masa de pizza", "Salsa de tomate",
                    "Mozzarella", "Pepperoni", "Papa", "Aceite", "Pechuga de pollo"]:
        i = session.exec(select(Ingrediente).where(Ingrediente.nombre == nombre)).first()
        if i:
            ing[nombre] = i

    # Busco categorias por nombre
    cats = {}
    for nombre in ["Hamburguesas", "Pizzas", "Bebidas", "Postres", "Papas y Acompanantes", "Ensaladas", "Parrilla"]:
        c = session.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
        if c:
            cats[nombre] = c

    productos_data = [
        {
            "nombre": "Clasica Burger",
            "descripcion": "Carne de res 200g, queso cheddar, lechuga, tomate y pan artesanal",
            "precio_base": 8500.0,
            "stock_cantidad": 50,
            "disponible": True,
            "imagenes_url": None,
            "categoria": "Hamburguesas",
            "ingredientes": [
                (ing["Carne de res"], 1, unid, False),
                (ing["Pan de hamburguesa"], 1, unid, False),
                (ing["Queso cheddar"], 2, unid, False),
                (ing["Lechuga"], 1, unid, True),
                (ing["Tomate"], 2, unid, True),
            ]
        },
        {
            "nombre": "Bacon Cheese Burger",
            "descripcion": "Carne de res, panceta crocante, queso cheddar, cebolla morada",
            "precio_base": 10500.0,
            "stock_cantidad": 30,
            "disponible": True,
            "imagenes_url": None,
            "categoria": "Hamburguesas",
            "ingredientes": [
                (ing["Carne de res"], 1, unid, False),
                (ing["Pan de hamburguesa"], 1, unid, False),
                (ing["Panceta"], 3, unid, True),
                (ing["Queso cheddar"], 2, unid, False),
                (ing["Cebolla"], 1, unid, True),
            ]
        },
        {
            "nombre": "Pizza Mozzarella",
            "descripcion": "Masa artesanal, salsa de tomate, mozzarella fresco y oregano",
            "precio_base": 12000.0,
            "stock_cantidad": 20,
            "disponible": True,
            "imagenes_url": None,
            "categoria": "Pizzas",
            "ingredientes": [
                (ing["Masa de pizza"], 1, unid, False),
                (ing["Salsa de tomate"], 1, unid, False),
                (ing["Mozzarella"], 200, g, False),
            ]
        },
        {
            "nombre": "Pizza Pepperoni",
            "descripcion": "Masa artesanal, salsa de tomate, mozzarella y pepperoni",
            "precio_base": 14000.0,
            "stock_cantidad": 15,
            "disponible": True,
            "imagenes_url": None,
            "categoria": "Pizzas",
            "ingredientes": [
                (ing["Masa de pizza"], 1, unid, False),
                (ing["Salsa de tomate"], 1, unid, False),
                (ing["Mozzarella"], 200, g, False),
                (ing["Pepperoni"], 100, g, True),
            ]
        },
        {
            "nombre": "Papas Fritas",
            "descripcion": "Papas fritas crujientes con sal marina",
            "precio_base": 4500.0,
            "stock_cantidad": 100,
            "disponible": True,
            "imagenes_url": None,
            "categoria": "Papas y Acompanantes",
            "ingredientes": [
                (ing["Papa"], 300, g, False),
                (ing["Aceite"], 50, mL, False),
            ]
        },
        {
            "nombre": "Ensalada Caesar",
            "descripcion": "Lechuga fresca, pollo grillé, croutons y aderezo Caesar",
            "precio_base": 9500.0,
            "stock_cantidad": 25,
            "disponible": True,
            "imagenes_url": None,
            "categoria": "Ensaladas",
            "ingredientes": [
                (ing["Lechuga"], 1, unid, False),
                (ing["Pechuga de pollo"], 200, g, False),
            ]
        },
    ]

    for p in productos_data:
        existe = session.exec(
            select(Producto).where(Producto.nombre == p["nombre"])
        ).first()
        if existe:
            print(f"  Producto ya existe: {p['nombre']}")
            continue

        ingred = p.pop("ingredientes")
        cat_nombre = p.pop("categoria")

        producto = Producto(**p)
        session.add(producto)
        session.flush()

        # Asigno categoria
        if cat_nombre in cats:
            pc = ProductoCategoria(producto_id=producto.id, categoria_id=cats[cat_nombre].id)
            session.add(pc)

        # Asigno ingredientes con cantidad y unidad
        for ing_obj, cantidad, unidad, removible in ingred:
            if ing_obj:
                pi = ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=ing_obj.id,
                    cantidad=cantidad,
                    unidad_medida_id=unidad.id if unidad else None,
                    es_removible=removible
                )
                session.add(pi)

        print(f"  Producto creado: {p['nombre']} (${p['precio_base']:,.0f})")


if __name__ == "__main__":
    run_seed()

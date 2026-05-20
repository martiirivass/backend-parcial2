from sqlmodel import Session, select
from app.db.database import engine
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.estado_pedido_model import EstadoPedido
from app.models.forma_pago_model import FormaPago
from app.auth.security import hash_password


def run_seed():
    with Session(engine) as session:
        seed_roles(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
        seed_admin(session)
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


def seed_estados_pedido(session):
    estados_data = [
        {"codigo": "PENDIENTE", "nombre": "Pendiente"},
        {"codigo": "CONFIRMADO", "nombre": "Confirmado"},
        {"codigo": "EN_PREP", "nombre": "En Preparacion"},
        {"codigo": "EN_CAMINO", "nombre": "En Camino"},
        {"codigo": "ENTREGADO", "nombre": "Entregado"},
        {"codigo": "CANCELADO", "nombre": "Cancelado"},
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
        {"codigo": "EFECTIVO", "nombre": "Efectivo", "descripcion": "Pago en efectivo al recibir"},
        {"codigo": "TARJETA", "nombre": "Tarjeta", "descripcion": "Debito o credito"},
        {"codigo": "TRANSFERENCIA", "nombre": "Transferencia", "descripcion": "Transferencia bancaria"},
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
            password=hash_password("admin123"),
            roles=[rol_admin]
        )
        session.add(admin)
        print("  Usuario admin creado: admin@admin.com / admin123")
    else:
        print("  Usuario admin ya existe")


if __name__ == "__main__":
    run_seed()

"""Fixtures compartidos para todos los tests de FASE 4."""
import uuid
from collections.abc import Generator
from decimal import Decimal
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db.database import engine, get_session
from app.main import app
from app.models.usuario import Usuario
from app.models.pedido_model import Pedido
from app.models.detalle_pedido_model import DetallePedido
from app.models.pago_model import Pago
from app.models.producto_model import Producto
from app.auth.security import create_access_token

# ═══════════════════════════════════════════════════════════════
# Session fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture
def db_rollback() -> Generator[Session, None, None]:
    """Function-scoped session. Sin transacción externa: datos
    commiteados son visibles desde otras sesiones (Session(engine)),
    cambios no commiteados se revierten al final."""
    connection = engine.connect()
    session = Session(bind=connection)

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = lambda: session

    yield session

    session.close()
    connection.rollback()
    connection.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(overrides)


# ═══════════════════════════════════════════════════════════════
# Token fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def admin_token(db: Session) -> Optional[str]:
    admin = db.exec(
        select(Usuario).where(Usuario.email == "admin@foodstore.com")
    ).first()
    if not admin:
        return None
    return create_access_token(data={"sub": str(admin.id)})


@pytest.fixture(scope="session")
def client_token(db: Session) -> Optional[str]:
    user = db.exec(
        select(Usuario).where(Usuario.email == "test@test.com")
    ).first()
    if not user:
        return None
    return create_access_token(data={"sub": str(user.id)})


# ═══════════════════════════════════════════════════════════════
# Data ID helpers (session-scoped — no mutan)
# ═══════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def producto_id(db: Session) -> Optional[int]:
    prod = db.exec(
        select(Producto).where(Producto.deleted_at.is_(None))
    ).first()
    return prod.id if prod else None


@pytest.fixture(scope="session")
def cliente_id(db: Session) -> Optional[int]:
    user = db.exec(
        select(Usuario).where(Usuario.email == "test@test.com")
    ).first()
    return user.id if user else None


# ═══════════════════════════════════════════════════════════════
# Test client
# ═══════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════
# Factory helpers
# ═══════════════════════════════════════════════════════════════


def make_pedido(
    db: Session,
    usuario_id: int,
    *,
    forma_pago_codigo: str = "EFECTIVO",
    subtotal: Decimal = Decimal("100.00"),
    descuento: Decimal = Decimal("0.00"),
    costo_envio: Decimal = Decimal("50.00"),
    total: Optional[Decimal] = None,
    estado_codigo: str = "PENDIENTE",
) -> Pedido:
    if total is None:
        total = subtotal - descuento + costo_envio
    pedido = Pedido(
        usuario_id=usuario_id,
        estado_codigo=estado_codigo,
        forma_pago_codigo=forma_pago_codigo,
        subtotal=subtotal,
        descuento=descuento,
        costo_envio=costo_envio,
        total=total,
    )
    db.add(pedido)
    db.flush()
    return pedido


def make_pago(
    db: Session,
    pedido_id: int,
    *,
    monto: Decimal = Decimal("100.00"),
    forma_pago_codigo: str = "EFECTIVO",
    external_reference: Optional[str] = None,
    mp_status: Optional[str] = "pending",
    mp_payment_id: Optional[int] = None,
) -> Pago:
    pago = Pago(
        pedido_id=pedido_id,
        monto=monto,
        forma_pago_codigo=forma_pago_codigo,
        external_reference=external_reference or uuid.uuid4().hex,
        mp_status=mp_status,
        mp_payment_id=mp_payment_id,
    )
    db.add(pago)
    db.flush()
    return pago


def make_detalle(
    db: Session,
    pedido_id: int,
    producto_id: int,
    *,
    cantidad: int = 1,
    precio_snapshot: Decimal = Decimal("100.00"),
) -> DetallePedido:
    detalle = DetallePedido(
        pedido_id=pedido_id,
        producto_id=producto_id,
        cantidad=cantidad,
        nombre_snapshot="Test Producto",
        precio_snapshot=precio_snapshot,
        subtotal_snap=precio_snapshot * cantidad,
    )
    db.add(detalle)
    db.flush()
    return detalle

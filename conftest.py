"""
Conftest compartido — helpers reutilizables para tests.

Provee inicialización común (DB session, UnitOfWork, repos) para evitar
duplicación en test_productos.py, test_soft_delete.py y test_integral.py.

USO:
    from conftest import get_db, make_uow, make_repos, create_test_user
"""

from sqlmodel import Session
from app.db.database import engine
from app.core.unit_of_work import UnitOfWork

# Repos
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.pedido_repository import PedidoRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository


def get_db() -> Session:
    """Crea y retorna una nueva sesión de BD."""
    return Session(engine)


def make_uow(db: Session) -> UnitOfWork:
    """Crea un UnitOfWork para la sesión dada."""
    return UnitOfWork(db)


def make_repos(db: Session) -> dict:
    """Crea todos los repositorios y los retorna en un dict."""
    return {
        "categoria": CategoriaRepository(db),
        "producto": ProductoRepository(db),
        "ingrediente": IngredienteRepository(db),
        "pedido": PedidoRepository(db),
        "refresh_token": RefreshTokenRepository(db),
    }


def create_test_user(db: Session, email: str = "test@test.com") -> object:
    """
    Crea un usuario CLIENT de prueba si no existe.
    Retorna el usuario (existente o recién creado).
    """
    from sqlmodel import select
    from app.models.usuario import Usuario
    from app.models.rol import Rol
    from app.models.usuario_rol_model import UsuarioRol
    from app.auth.services import register_user

    # Verificar si ya existe
    exists = db.exec(select(Usuario).where(Usuario.email == email)).first()
    if exists:
        return exists

    # Crear nuevo
    try:
        cliente = register_user(
            nombre="Test",
            apellido="Test",
            email=email,
            password="test123",
            session=db
        )
        db.commit()
        db.refresh(cliente)
        return cliente
    except Exception:
        db.rollback()
        return None

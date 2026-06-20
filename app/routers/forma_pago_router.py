from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.forma_pago_schema import FormaPagoRead
from app.services.forma_pago_service import FormaPagoService

router = APIRouter(
    prefix="/formas-pago",
    tags=["Catálogos"]
)


@router.get("/", response_model=list[FormaPagoRead])
def listar(db: Session = Depends(get_session)):
    """Lista todas las formas de pago."""
    service = FormaPagoService(db)

    return service.listar()


@router.get("/{codigo}", response_model=FormaPagoRead)
def obtener(codigo: str, db: Session = Depends(get_session)):
    """Obtiene una forma de pago por su código."""
    service = FormaPagoService(db)

    return service.obtener(codigo)

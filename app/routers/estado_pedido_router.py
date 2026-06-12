from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.estado_pedido_schema import EstadoPedidoRead
from app.services.estado_pedido_service import EstadoPedidoService

router = APIRouter(
    prefix="/estados-pedido",
    tags=["Catálogos"]
)


@router.get("/", response_model=list[EstadoPedidoRead])
def listar(db: Session = Depends(get_session)):

    service = EstadoPedidoService(db)

    return service.listar()


@router.get("/{codigo}", response_model=EstadoPedidoRead)
def obtener(codigo: str, db: Session = Depends(get_session)):

    service = EstadoPedidoService(db)

    return service.obtener(codigo)

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.database import get_session
from app.schemas.estado_pedido_schema import EstadoPedidoRead
from app.models.estado_pedido_model import EstadoPedido

router = APIRouter(
    prefix="/estados-pedido",
    tags=["Catálogos"]
)


@router.get("/", response_model=list[EstadoPedidoRead])
def listar(db: Session = Depends(get_session)):
    return db.exec(select(EstadoPedido)).all()


@router.get("/{codigo}", response_model=EstadoPedidoRead)
def obtener(codigo: str, db: Session = Depends(get_session)):
    ep = db.exec(select(EstadoPedido).where(EstadoPedido.codigo == codigo)).first()
    if not ep:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Estado de pedido no encontrado")
    return ep

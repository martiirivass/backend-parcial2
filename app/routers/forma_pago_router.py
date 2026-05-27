from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.database import get_session
from app.schemas.forma_pago_schema import FormaPagoRead
from app.models.forma_pago_model import FormaPago

router = APIRouter(
    prefix="/formas-pago",
    tags=["Catálogos"]
)


@router.get("/", response_model=list[FormaPagoRead])
def listar(db: Session = Depends(get_session)):
    return db.exec(select(FormaPago)).all()


@router.get("/{codigo}", response_model=FormaPagoRead)
def obtener(codigo: str, db: Session = Depends(get_session)):
    fp = db.exec(select(FormaPago).where(FormaPago.codigo == codigo)).first()
    if not fp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Forma de pago no encontrada")
    return fp

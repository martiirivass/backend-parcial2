from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.database import get_session
from app.schemas.unidad_medida_schema import (
    UnidadMedidaCreate,
    UnidadMedidaRead,
    UnidadMedidaUpdate
)
from app.models.unidad_medida_model import UnidadMedida
from app.auth.permissions import require_roles
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/unidades-medida",
    tags=["Catálogos"]
)


@router.get("/", response_model=list[UnidadMedidaRead])
def listar(db: Session = Depends(get_session)):
    return db.exec(select(UnidadMedida)).all()


@router.get("/{unidad_id}", response_model=UnidadMedidaRead)
def obtener(unidad_id: int, db: Session = Depends(get_session)):
    unidad = db.get(UnidadMedida, unidad_id)
    if not unidad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return unidad


@router.post("/", response_model=UnidadMedidaRead, status_code=201)
def crear(
    datos: UnidadMedidaCreate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN", "STOCK"))
):
    unidad = UnidadMedida(**datos.model_dump())
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


@router.put("/{unidad_id}", response_model=UnidadMedidaRead)
def actualizar(
    unidad_id: int,
    datos: UnidadMedidaUpdate,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN", "STOCK"))
):
    unidad = db.get(UnidadMedida, unidad_id)
    if not unidad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    for key, val in datos.model_dump(exclude_unset=True).items():
        setattr(unidad, key, val)
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


@router.delete("/{unidad_id}", status_code=204)
def eliminar(
    unidad_id: int,
    db: Session = Depends(get_session),
    current_user: Usuario = Depends(require_roles("ADMIN"))
):
    unidad = db.get(UnidadMedida, unidad_id)
    if not unidad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    db.delete(unidad)
    db.commit()

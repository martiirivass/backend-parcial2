from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import Session

from app.db.database import get_session

from app.schemas.ingrediente_schema import (
    IngredienteCreate,
    IngredienteUpdate,
    IngredienteRead
)

from app.services.ingrediente_service import IngredienteService

router = APIRouter(
    prefix="/ingredientes",
    tags=["Ingredientes"]
)


# Crear ingrediente
@router.post("/", response_model=IngredienteRead, status_code=201)
def crear(
    ingrediente: IngredienteCreate,
    db: Session = Depends(get_session)
):
    service = IngredienteService(db)

    return service.crear_ingrediente(ingrediente)


# Listar ingredientes
@router.get("/")
def listar(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_session)
):
    service = IngredienteService(db)

    return service.listar_ingredientes(limit, offset)


# Obtener ingrediente
@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def obtener(
    ingrediente_id: int,
    db: Session = Depends(get_session)
):
    service = IngredienteService(db)

    return service.obtener_ingrediente(ingrediente_id)


# Actualizar ingrediente
@router.put("/{ingrediente_id}", response_model=IngredienteRead)
def actualizar(
    ingrediente_id: int,
    datos: IngredienteUpdate,
    db: Session = Depends(get_session)
):
    service = IngredienteService(db)

    return service.actualizar_ingrediente(ingrediente_id, datos)


# Eliminar ingrediente
@router.delete("/{ingrediente_id}", status_code=204)
def eliminar(
    ingrediente_id: int,
    db: Session = Depends(get_session)
):
    service = IngredienteService(db)

    service.eliminar_ingrediente(ingrediente_id)
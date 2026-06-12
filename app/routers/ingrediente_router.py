from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.auth.permissions import require_roles
from app.db.database import get_session

from app.schemas.ingrediente_schema import (
    IngredienteCreate,
    IngredienteUpdate,
    IngredienteRead
)

from app.services.ingrediente_service import (
    IngredienteService
)

from app.core.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/ingredientes",
    tags=["Ingredientes"]
)


# Crear ingrediente
@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=201
)
def crear(
    ingrediente: IngredienteCreate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN", "STOCK")
    )
):

    with UnitOfWork(db):

        service = IngredienteService(db)

        nuevo = service.crear_ingrediente(
            ingrediente
        )

        db.refresh(nuevo)

        return nuevo


# Listar ingredientes
@router.get(
    "/",
    response_model=list[IngredienteRead],
    summary="Listar ingredientes"
)
def listar(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    q: str | None = Query(
        None,
        description="Buscar ingrediente"
    ),
    db: Session = Depends(get_session)
):

    service = IngredienteService(db)

    return service.listar_ingredientes(
    limit,
    offset,
    q
)


# Obtener ingrediente
@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteRead
)
def obtener(
    ingrediente_id: int,
    db: Session = Depends(get_session)
):

    service = IngredienteService(db)

    return service.obtener_ingrediente(
        ingrediente_id
    )


# Actualizar ingrediente
@router.put(
    "/{ingrediente_id}",
    response_model=IngredienteRead
)
def actualizar(
    ingrediente_id: int,
    datos: IngredienteUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN", "STOCK")
    )
):

    with UnitOfWork(db):

        service = IngredienteService(db)

        ingrediente = service.actualizar_ingrediente(
            ingrediente_id,
            datos
        )

        db.refresh(ingrediente)

        return ingrediente


# Eliminar ingrediente
@router.delete(
    "/{ingrediente_id}",
    status_code=204
)
def eliminar(
    ingrediente_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = IngredienteService(db)

        service.eliminar_ingrediente(
            ingrediente_id
        )

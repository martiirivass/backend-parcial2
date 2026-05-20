from fastapi import APIRouter, Query, Depends
from typing import Annotated, Optional
from sqlmodel import Session

from app.db.database import get_session

from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaRead
)

from app.services.categoria_service import CategoriaService
from app.auth.permissions import require_roles

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)


# Crear categoría (solo ADMIN)
@router.post("/", response_model=CategoriaRead, status_code=201)
def crear(
    categoria: CategoriaCreate,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = CategoriaService(db)

    return service.crear_categoria(categoria)


# Listar categorías con filtro por parent_id (publico)
@router.get("/")
def listar(
    limit: Annotated[int, Query(le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    parent_id: Optional[int] = Query(None, description="Filtrar por categoria padre"),
    db: Session = Depends(get_session)
):
    service = CategoriaService(db)

    return service.listar_categorias(limit, offset, parent_id=parent_id)


# Obtener categoría (publico)
@router.get("/{categoria_id}", response_model=CategoriaRead)
def obtener(
    categoria_id: int,
    db: Session = Depends(get_session)
):
    service = CategoriaService(db)

    return service.obtener_categoria(categoria_id)


# Actualizar categoría (solo ADMIN)
@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar(
    categoria_id: int,
    datos: CategoriaUpdate,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = CategoriaService(db)

    return service.actualizar_categoria(categoria_id, datos)


# Eliminar categoría (solo ADMIN)
@router.delete("/{categoria_id}", status_code=204)
def eliminar(
    categoria_id: int,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = CategoriaService(db)

    service.eliminar_categoria(categoria_id)

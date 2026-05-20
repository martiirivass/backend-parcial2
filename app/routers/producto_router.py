# producto_router.py

from fastapi import APIRouter, Depends, Query
from typing import Annotated
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.producto_schema import (
    ProductoCreate,
    ProductoUpdate,
    ProductoReadWithRelations
)
 
from app.services.producto_service import ProductoService

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# Crear producto
@router.post("/", response_model=ProductoReadWithRelations, status_code=201)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.crear_producto(producto)

# Listar productos con paginación
@router.get("/")
def listar(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.listar_productos(limit, offset)

# Obtener producto por ID
@router.get("/{producto_id}", response_model=ProductoReadWithRelations)
def obtener(
    producto_id: int,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.obtener_producto(producto_id)


# Actualizar producto
@router.put("/{producto_id}", response_model=ProductoReadWithRelations)
def actualizar(
    producto_id: int,
    datos: ProductoUpdate,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.actualizar_producto(producto_id, datos)

# Eliminar producto
@router.delete("/{producto_id}", status_code=204)
def eliminar(
    producto_id: int,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    service.eliminar_producto(producto_id)
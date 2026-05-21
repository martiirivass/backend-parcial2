from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import Annotated, Optional
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.producto_schema import (
    ProductoCreate,
    ProductoUpdate,
    ProductoReadWithRelations,
    ProductoDisponibilidadUpdate
)
 
from app.services.producto_service import ProductoService
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# Crear producto (solo ADMIN)
@router.post("/", response_model=ProductoReadWithRelations, status_code=201)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = ProductoService(db)

    return service.crear_producto(producto)

# Listar productos con filtros y paginacion (publico)
@router.get("/")
def listar(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    q: Optional[str] = Query(None, description="Buscar por nombre o descripcion"),
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.listar_productos(
        limit, offset,
        categoria_id=categoria_id,
        disponible=disponible,
        q=q
    )

# Obtener producto por ID (publico)
@router.get("/{producto_id}", response_model=ProductoReadWithRelations)
def obtener(
    producto_id: int,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.obtener_producto(producto_id)

# Actualizar disponibilidad y stock (ADMIN y STOCK)
@router.patch("/{producto_id}/disponibilidad", response_model=ProductoReadWithRelations)
def actualizar_disponibilidad(
    producto_id: int,
    datos: ProductoDisponibilidadUpdate,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN", "STOCK"))
):
    service = ProductoService(db)

    return service.actualizar_disponibilidad(producto_id, datos)

# Actualizar producto (solo ADMIN)
@router.put("/{producto_id}", response_model=ProductoReadWithRelations)
def actualizar(
    producto_id: int,
    datos: ProductoUpdate,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = ProductoService(db)

    return service.actualizar_producto(producto_id, datos)

# Eliminar producto (solo ADMIN)
@router.delete("/{producto_id}", status_code=204)
def eliminar(
    producto_id: int,
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = ProductoService(db)

    service.eliminar_producto(producto_id)

# Subir imagen de producto (solo ADMIN)
@router.post("/{producto_id}/imagen", response_model=ProductoReadWithRelations)
def subir_imagen(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user = Depends(require_roles("ADMIN"))
):
    service = ProductoService(db)

    return service.subir_imagen(producto_id, archivo)

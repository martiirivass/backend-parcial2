from typing import (
    Annotated,
    Optional
)

from fastapi import (
    APIRouter,
    Depends,
    Query,
    UploadFile,
    File
)

from sqlmodel import Session

from app.auth.permissions import require_roles
from app.db.database import get_session

from app.schemas.producto_schema import (
    ProductoCreate,
    ProductoUpdate,
    ProductoReadWithRelations,
    ProductoImagenesUpdate,
    ProductoDisponibilidadUpdate
)

from app.services.producto_service import (
    ProductoService
)

from app.core.unit_of_work import UnitOfWork

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


# Crear producto
@router.post(
    "/",
    response_model=ProductoReadWithRelations,
    status_code=201
)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = ProductoService(db)

        nuevo = service.crear_producto(
            producto
        )

    db.refresh(nuevo)

    return nuevo


# Listar productos
@router.get("/")
def listar(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    categoria_id: Optional[int] = Query(
        None,
        description="Filtrar por categoria"
    ),
    disponible: Optional[bool] = Query(
        None,
        description="Filtrar por disponibilidad"
    ),
    q: Optional[str] = Query(
        None,
        description="Buscar por nombre o descripcion"
    ),
    db: Session = Depends(get_session)
):

    service = ProductoService(db)

    return service.listar_productos(
        limit=limit,
        offset=offset,
        categoria_id=categoria_id,
        disponible=disponible,
        q=q
    )


# Obtener producto
@router.get(
    "/{producto_id}",
    response_model=ProductoReadWithRelations
)
def obtener(
    producto_id: int,
    db: Session = Depends(get_session)
):

    service = ProductoService(db)

    return service.obtener_producto(
        producto_id
    )


# Actualizar disponibilidad
@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoReadWithRelations
)
def actualizar_disponibilidad(
    producto_id: int,
    datos: ProductoDisponibilidadUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN", "STOCK")
    )
):

    with UnitOfWork(db):

        service = ProductoService(db)

        producto = service.actualizar_disponibilidad(
            producto_id,
            datos
        )

        db.refresh(producto)

        return producto


# Actualizar lista de imágenes
@router.patch(
    "/{producto_id}/imagenes",
    response_model=ProductoReadWithRelations
)
def actualizar_imagenes(
    producto_id: int,
    datos: ProductoImagenesUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = ProductoService(db)

        producto = service.actualizar_imagenes(
            producto_id,
            datos.imagenes_url
        )

        db.refresh(producto)

        return producto


# Actualizar producto
@router.put(
    "/{producto_id}",
    response_model=ProductoReadWithRelations
)
def actualizar(
    producto_id: int,
    datos: ProductoUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = ProductoService(db)

        producto = service.actualizar_producto(
            producto_id,
            datos
        )

        db.refresh(producto)

        return producto


# Eliminar producto
@router.delete(
    "/{producto_id}",
    status_code=204
)
def eliminar(
    producto_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = ProductoService(db)

        service.eliminar_producto(
            producto_id
        )


# Subir imagen
@router.post(
    "/{producto_id}/imagen",
    response_model=ProductoReadWithRelations
)
def subir_imagen(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):

    with UnitOfWork(db):

        service = ProductoService(db)

        producto = service.subir_imagen(
            producto_id,
            archivo
        )

        db.flush()
        db.refresh(producto)

        return producto

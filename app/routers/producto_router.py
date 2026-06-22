import json
import logging

from decimal import Decimal
from typing import (
    Annotated,
    Optional
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    UploadFile,
    File,
    Form
)

from sqlmodel import Session

from app.auth.permissions import require_roles
from app.core.config import cloudinary_configurado
from app.db.database import get_session

from app.schemas.ingrediente_schema import IngredienteRead

from app.schemas.producto_schema import (
    ProductoCreate,
    ProductoUpdate,
    ProductoReadWithRelations,
    ProductoImagenesUpdate,
    ProductoDisponibilidadUpdate,
    ProductoIngredienteCreate,
    ProductoIngredienteRead
)

from app.services.cloudinary_service import (
    CloudinaryService
)

from app.services.producto_service import (
    ProductoService
)

from app.core.limiter import limiter
from app.core.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

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
@limiter.limit("10/minute")
def listar(
    request: Request,
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

    page = (offset // limit) + 1 if limit > 0 else 1
    size = limit

    return service.listar_productos(
        page=page,
        size=size,
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

        return producto


# Listar ingredientes de un producto
@router.get(
    "/{producto_id}/ingredientes",
    response_model=list[IngredienteRead]
)
def listar_ingredientes(
    producto_id: int,
    db: Session = Depends(get_session)
):
    service = ProductoService(db)

    return service.obtener_ingredientes(
        producto_id
    )


# Agregar ingrediente a producto
@router.post(
    "/{producto_id}/ingredientes",
    response_model=ProductoIngredienteRead,
    status_code=201
)
def agregar_ingrediente(
    producto_id: int,
    data: ProductoIngredienteCreate,
    db: Session = Depends(get_session),
    current_user=Depends(
        require_roles("ADMIN")
    )
):
    with UnitOfWork(db):

        service = ProductoService(db)

        return service.agregar_ingrediente(
            producto_id,
            data
        )


# ── Nuevos endpoints multipart/form-data para Cloudinary ──


@router.post(
    "/con-imagen",
    response_model=ProductoReadWithRelations,
    status_code=201,
    summary="Crear producto con imagen (multipart/form-data)",
    description=(
        "Crea un producto y opcionalmente sube una imagen "
        "en un solo request usando multipart/form-data. "
        "Los campos categoria_ids e ingrediente_ids se envían "
        "como strings JSON (ej. '[1,2]')."
    )
)
async def crear_producto_con_imagen(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio_base: Decimal = Form(...),
    stock_cantidad: int = Form(0),
    disponible: bool = Form(True),
    categoria_ids: str = Form(...),
    ingrediente_ids: str = Form(...),
    imagen: Optional[UploadFile] = File(None),
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):
    """
    Crea un producto recibiendo los datos como multipart/form-data
    (en lugar de JSON), ideal para incluir una imagen en el mismo request.

    - `categoria_ids` e `ingrediente_ids` se envían como strings
      con formato JSON array, e.g. `"[1, 2]"`
    - `imagen` es opcional; si no se envía, el producto se crea sin imagen
    """
    # Parse JSON arrays from string
    cat_ids = json.loads(categoria_ids)
    ing_ids = json.loads(ingrediente_ids)

    if not cat_ids or len(cat_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos una categoría"
        )
    if not ing_ids or len(ing_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un ingrediente"
        )

    producto_data = ProductoCreate(
        nombre=nombre,
        descripcion=descripcion,
        precio_base=precio_base,
        stock_cantidad=stock_cantidad,
        disponible=disponible,
        categoria_ids=cat_ids,
        ingrediente_ids=ing_ids,
    )

    with UnitOfWork(db):
        service = ProductoService(db)
        nuevo = service.crear_producto(producto_data)

        if imagen and imagen.filename:
            db.flush()
            nuevo = service.subir_imagen(nuevo.id, imagen)

    db.refresh(nuevo)
    return nuevo


@router.put(
    "/{producto_id}/con-imagen",
    response_model=ProductoReadWithRelations,
    summary="Actualizar producto con imagen (multipart/form-data)",
    description=(
        "Actualiza un producto y opcionalmente reemplaza su imagen "
        "usando multipart/form-data. "
        "Usar `eliminar_imagen=true` para borrar la imagen existente "
        "sin reemplazarla."
    )
)
async def actualizar_producto_con_imagen(
    producto_id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio_base: Optional[Decimal] = Form(None),
    stock_cantidad: Optional[int] = Form(None),
    disponible: Optional[bool] = Form(None),
    categoria_ids: Optional[str] = Form(None),
    ingrediente_ids: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    eliminar_imagen: Optional[bool] = Form(False),
    db: Session = Depends(get_session),
    current_user=Depends(require_roles("ADMIN"))
):
    """
    Actualiza un producto recibiendo los datos como multipart/form-data.

    - Solo se actualizan los campos enviados (todos son opcionales)
    - `categoria_ids` e `ingrediente_ids` se envían como strings
      con formato JSON array, e.g. `"[1, 2]"`
    - Si se envía `imagen`, se reemplaza la imagen existente
    - Si `eliminar_imagen=true` y NO se envía imagen,
      se elimina la imagen actual
    """
    # Build update dict from form fields
    update_dict = {}
    if nombre is not None:
        update_dict["nombre"] = nombre
    if descripcion is not None:
        update_dict["descripcion"] = descripcion
    if precio_base is not None:
        update_dict["precio_base"] = precio_base
    if stock_cantidad is not None:
        update_dict["stock_cantidad"] = stock_cantidad
    if disponible is not None:
        update_dict["disponible"] = disponible
    if categoria_ids is not None:
        update_dict["categoria_ids"] = json.loads(categoria_ids)
    if ingrediente_ids is not None:
        update_dict["ingrediente_ids"] = json.loads(ingrediente_ids)

    producto_data = ProductoUpdate(**update_dict)

    # ── DEBUG LOGGING ──
    logger.info("=== DEBUG actualizar_producto_con_imagen ===")
    logger.info(f"producto_id={producto_id}")
    logger.info(f"imagen is None? {imagen is None}")
    if imagen:
        logger.info(f"imagen.filename={repr(imagen.filename)}")
        logger.info(f"imagen.content_type={repr(imagen.content_type)}")
    logger.info(f"eliminar_imagen={eliminar_imagen}")
    logger.info(f"update_dict keys: {list(update_dict.keys())}")
    logger.info(f"Cloudinary configurado: {cloudinary_configurado()}")
    logger.info(f"ProductoUpdate fields: {update_dict}")
    # ── END DEBUG ──

    with UnitOfWork(db):
        service = ProductoService(db)

        # If new image provided, delete old Cloudinary image first
        if imagen and imagen.filename:
            producto = service.obtener_producto(producto_id)
            logger.info(f"Producto actual tiene imagen_public_id: {producto.imagen_public_id}")
            if producto.imagen_public_id and cloudinary_configurado():
                try:
                    CloudinaryService.eliminar(
                        producto.imagen_public_id
                    )
                    logger.info(f"Imagen Cloudinary eliminada: {producto.imagen_public_id}")
                except Exception as e:
                    logger.warning(
                        f"Error al eliminar imagen anterior "
                        f"de Cloudinary: {e}"
                    )

        # Update product data
        producto = service.actualizar_producto(
            producto_id,
            producto_data
        )
        logger.info(f"After actualizar_producto: imagenes_url={producto.imagenes_url}")

        # Upload new image if provided
        if imagen and imagen.filename:
            logger.info(f"Calling subir_imagen for producto {producto_id}")
            try:
                producto = service.subir_imagen(producto_id, imagen)
                logger.info(f"After subir_imagen: imagenes_url={producto.imagenes_url}, imagen_url={producto.imagen_url}")
            except Exception as e:
                logger.error(f"Error en subir_imagen: {e}", exc_info=True)
                raise
        else:
            logger.info(f"subir_imagen NOT called: imagen={imagen is not None}, filename={imagen.filename if imagen else 'N/A'}")

        # If eliminar_imagen flag is set and no new image
        if eliminar_imagen and not (imagen and imagen.filename):
            logger.info("Eliminando imagen (eliminar_imagen flag)")
            if producto.imagen_public_id and cloudinary_configurado():
                try:
                    CloudinaryService.eliminar(
                        producto.imagen_public_id
                    )
                except Exception as e:
                    logger.warning(
                        f"Error al eliminar imagen de Cloudinary: {e}"
                    )
            producto.imagenes_url = None
            producto.imagen_public_id = None
            service.repo.update(producto)

    # Refresh outside UnitOfWork after commit
    db.refresh(producto)
    logger.info(f"Final response: imagen_url={producto.imagen_url}, imagenes_url={producto.imagenes_url}")
    return producto

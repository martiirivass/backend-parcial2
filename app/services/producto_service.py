import logging
import math
import uuid

from pathlib import Path

from fastapi import UploadFile

from app.core.errors import http_error as http_error

from app.core.config import cloudinary_configurado

from app.models.producto_model import Producto

from app.repositories.producto_repository import (
    ProductoRepository
)

from app.repositories.categoria_repository import (
    CategoriaRepository
)

from app.repositories.ingrediente_repository import (
    IngredienteRepository
)

from app.schemas.producto_schema import (
    ProductoReadWithRelations
)

from app.core.config import UPLOADS_DIR
from app.services.imagen_service import (
    ImagenService
)

from app.services.cloudinary_service import (
    CloudinaryService
)

logger = logging.getLogger(__name__)


class ProductoService:

    def __init__(self, db):

        self.repo = ProductoRepository(db)

        self.cat_repo = CategoriaRepository(db)

        self.ing_repo = IngredienteRepository(db)

    # Crear producto
    def crear_producto(
        self,
        producto_data
    ):

        data = producto_data.model_dump(
            exclude={
                "categoria_ids",
                "ingrediente_ids"
            }
        )

        nuevo = Producto(**data)

        if producto_data.categoria_ids:

            categorias = [
                self.cat_repo.get_by_id(cid)
                for cid in producto_data.categoria_ids
            ]

            nuevo.categorias = [
                categoria
                for categoria in categorias
                if categoria
            ]

        if producto_data.ingrediente_ids:

            ingredientes = [
                self.ing_repo.get_by_id(iid)
                for iid in producto_data.ingrediente_ids
            ]

            nuevo.ingredientes = [
                ingrediente
                for ingrediente in ingredientes
                if ingrediente
            ]

        self.repo.create(nuevo)

        return nuevo

    # Obtener producto
    def obtener_producto(
        self,
        producto_id: int
    ):

        producto = self.repo.get_by_id(
            producto_id
        )

        if not producto:
            raise http_error(
                404, "Producto no encontrado", "PRODUCT_NOT_FOUND"
            )

        return producto

    # Listar productos
    def listar_productos(
        self,
        page: int = 1,
        size: int = 20,
        categoria_id=None,
        disponible=None,
        q=None
    ):

        skip = (page - 1) * size

        productos = self.repo.get_all_filtered(
            limit=size,
            offset=skip,
            categoria_id=categoria_id,
            disponible=disponible,
            q=q
        )

        total = self.repo.count_filtered(
            categoria_id=categoria_id,
            disponible=disponible,
            q=q
        )

        data = [
            ProductoReadWithRelations.model_validate(
                producto
            )
            for producto in productos
        ]

        pages = math.ceil(total / size) if size > 0 else 0

        return {
            "data": data,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

    # Actualizar disponibilidad
    def actualizar_disponibilidad(
        self,
        producto_id,
        datos
    ):

        producto = self.repo.get_by_id(
            producto_id
        )

        if not producto:
            raise http_error(
                404, "Producto no encontrado", "PRODUCT_NOT_FOUND"
            )

        producto.disponible = datos.disponible

        if datos.stock_cantidad is not None:
            producto.stock_cantidad = (
                datos.stock_cantidad
            )

        self.repo.update(producto)

        return producto

    # Actualizar producto
    def actualizar_producto(
        self,
        producto_id,
        datos
    ):

        producto = self.repo.get_by_id(
            producto_id
        )

        if not producto:
            raise http_error(
                404, "Producto no encontrado", "PRODUCT_NOT_FOUND"
            )

        update_data = datos.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            if key not in (
                "categoria_ids",
                "ingrediente_ids"
            ):
                setattr(producto, key, value)

        # Categorías
        if (
            hasattr(datos, "categoria_ids")
            and datos.categoria_ids is not None
        ):

            categorias = [
                self.cat_repo.get_by_id(cid)
                for cid in datos.categoria_ids
            ]

            producto.categorias = [
                categoria
                for categoria in categorias
                if categoria
            ]

        # Ingredientes
        if (
            hasattr(datos, "ingrediente_ids")
            and datos.ingrediente_ids is not None
        ):

            ingredientes = [
                self.ing_repo.get_by_id(iid)
                for iid in datos.ingrediente_ids
            ]

            producto.ingredientes = [
                ingrediente
                for ingrediente in ingredientes
                if ingrediente
            ]

        self.repo.update(producto)

        return producto

    # Eliminar producto
    def eliminar_producto(
        self,
        producto_id
    ):

        producto = self.repo.get_by_id(
            producto_id
        )

        if not producto:
            raise http_error(
                404, "Producto no encontrado", "PRODUCT_NOT_FOUND"
            )

        # Delete image from Cloudinary if present
        if producto.imagen_public_id and cloudinary_configurado():
            try:
                CloudinaryService.eliminar(producto.imagen_public_id)
            except Exception as e:
                logger.warning(
                    f"Error al eliminar imagen de Cloudinary: {e}"
                )

        self.repo.delete(producto)

    # Actualizar lista de imágenes
    def actualizar_imagenes(
        self,
        producto_id: int,
        imagenes_url: list[str]
    ):
        producto = self.repo.get_by_id(producto_id)

        if not producto:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        producto.imagenes_url = imagenes_url
        self.repo.update(producto)

        # ── debug
        logger.info(f"subir_imagen: setting imagenes_url={producto.imagenes_url}")
        # ──

        return producto
    # Subir imagen
    def subir_imagen(
        self,
        producto_id: int,
        archivo: UploadFile
    ):

        producto = self.repo.get_by_id(
            producto_id
        )

        if not producto:
            raise http_error(
                404, "Producto no encontrado", "PRODUCT_NOT_FOUND"
            )

        logger.info(f"subir_imagen called: producto_id={producto_id}, filename={repr(archivo.filename)}, content_type={repr(archivo.content_type)}")

        # Read file content
        contenido = archivo.file.read()
        logger.info(f"File read: {len(contenido)} bytes")

        # Validate
        content_type = archivo.content_type or "application/octet-stream"
        CloudinaryService.validar_imagen(contenido, content_type)

        # Generate public_id
        ext = Path(archivo.filename).suffix if archivo.filename else ".jpg"
        public_id = f"{uuid.uuid4().hex}{ext}"

        if cloudinary_configurado():
            # Cloudinary path — captures public_id for future cleanup
            resultado = CloudinaryService.subir(
                contenido,
                public_id=public_id,
                folder="foodstore/productos"
            )
            producto.imagenes_url = [resultado["secure_url"]]
            producto.imagen_public_id = resultado["public_id"]
        else:
            # Local fallback — save directly (bytes already read)
            nombre_archivo = f"{producto_id}_{uuid.uuid4().hex}{ext}"
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            ruta = UPLOADS_DIR / nombre_archivo
            with open(ruta, "wb") as f:
                f.write(contenido)
            producto.imagenes_url = [f"http://localhost:8000/uploads/{nombre_archivo}"]

        self.repo.update(producto)

        return producto

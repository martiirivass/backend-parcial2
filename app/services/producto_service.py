import logging

import math

from fastapi import UploadFile

from app.core.errors import http_error as http_error

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

from app.services.imagen_service import (
    ImagenService
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
            "items": data,
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

        imagen_url = ImagenService.guardar(
            producto_id,
            archivo
        )

        producto.imagenes_url = [imagen_url]

        self.repo.update(producto)

        return producto

import logging
from fastapi import HTTPException, UploadFile

from app.models.producto_model import Producto
from app.repositories.producto_repository import ProductoRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.services.imagen_service import guardar_imagen
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ProductoService:

    def __init__(self, db):
        self.db = db
        self.repo = ProductoRepository(db)
        self.cat_repo = CategoriaRepository(db)
        self.ing_repo = IngredienteRepository(db)
        self.uow = UnitOfWork(db)

    def crear_producto(self, producto_data):

        try:
            # Uso model_dump para pasar todos los campos de una
            data = producto_data.model_dump(exclude={"categoria_ids", "ingrediente_ids"})
            nuevo = Producto(**data)

            if producto_data.categoria_ids:
                categorias = [
                    self.cat_repo.get_by_id(cid)
                    for cid in producto_data.categoria_ids
                ]

                nuevo.categorias = [c for c in categorias if c]

            if producto_data.ingrediente_ids:
                ingredientes = [
                    self.ing_repo.get_by_id(iid)
                    for iid in producto_data.ingrediente_ids
                ]

                nuevo.ingredientes = [i for i in ingredientes if i]

            self.repo.create(nuevo)

            self.uow.commit()
            self.db.refresh(nuevo)

            return nuevo

        except Exception as e:
            logger.exception(f"Error creating producto: {e}")
            self.uow.rollback()
            raise

    def obtener_producto(self, producto_id):

        producto = self.repo.get_by_id(producto_id)

        if not producto:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        return producto

    def listar_productos(self, limit, offset, categoria_id=None, disponible=None, q=None):

        productos = self.repo.get_all_filtered(
            categoria_id=categoria_id,
            disponible=disponible,
            q=q
        )

        return {
            "data": productos[offset: offset + limit],
            "total": len(productos)
        }

    def actualizar_disponibilidad(self, producto_id, datos):

        try:
            producto = self.repo.get_by_id(producto_id)

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            producto.disponible = datos.disponible

            if datos.stock_cantidad is not None:
                producto.stock_cantidad = datos.stock_cantidad

            self.repo.update(producto)

            self.uow.commit()
            self.db.refresh(producto)

            return producto

        except Exception as e:
            logger.exception(f"Error updating disponibilidad: {e}")
            self.uow.rollback()
            raise

    def actualizar_producto(self, producto_id, datos):

        try:
            producto = self.repo.get_by_id(producto_id)

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            update_data = datos.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key not in ("categoria_ids", "ingrediente_ids"):
                    setattr(producto, key, value)

            # Actualizar categorias si viene
            if hasattr(datos, "categoria_ids") and datos.categoria_ids is not None:
                categorias = [
                    self.cat_repo.get_by_id(cid)
                    for cid in datos.categoria_ids
                ]
                producto.categorias = [c for c in categorias if c]

            # Actualizar ingredientes si viene
            if hasattr(datos, "ingrediente_ids") and datos.ingrediente_ids is not None:
                ingredientes = [
                    self.ing_repo.get_by_id(iid)
                    for iid in datos.ingrediente_ids
                ]
                producto.ingredientes = [i for i in ingredientes if i]

            self.repo.update(producto)

            self.uow.commit()
            self.db.refresh(producto)

            return producto

        except Exception as e:
            logger.exception(f"Error updating producto: {e}")
            self.uow.rollback()
            raise

    def eliminar_producto(self, producto_id):

        try:
            producto = self.repo.get_by_id(producto_id)

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            self.repo.delete(producto)

            self.uow.commit()

        except Exception as e:
            logger.exception(f"Error deleting producto: {e}")
            self.uow.rollback()
            raise

    def subir_imagen(self, producto_id: int, archivo: UploadFile):
        try:
            producto = self.repo.get_by_id(producto_id)

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            # Guardar imagen en disco y obtener URL
            imagen_url = guardar_imagen(producto_id, archivo)

            # Actualizar campo en DB
            producto.imagenes_url = imagen_url
            self.repo.update(producto)

            self.uow.commit()
            self.db.refresh(producto)

            return producto

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error subiendo imagen: {e}")
            self.uow.rollback()
            raise

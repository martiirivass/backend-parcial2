# app/services/producto_service.py

import logging
from fastapi import HTTPException

from app.models.producto_model import Producto
from app.repositories.producto_repository import ProductoRepository
from app.repositories.category_repository import CategoriaRepository
from app.repositories.ingredient_repository import IngredienteRepository
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

            nuevo = Producto(
                nombre=producto_data.nombre,
                descripcion=producto_data.descripcion,
                precio=producto_data.precio
            )

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

    def listar_productos(self, limit, offset):

        productos = self.repo.get_all()

        return {
            "data": productos[offset: offset + limit],
            "total": len(productos)
        }

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
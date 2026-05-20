import logging

from fastapi import HTTPException
from sqlmodel import select

from app.models.categoria_model import Categoria
from app.models.producto_categoria_model import ProductoCategoria
from app.repositories.categoria_repository import CategoriaRepository
from app.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class CategoriaService:

    def __init__(self, db):
        self.db = db
        self.repo = CategoriaRepository(db)
        self.uow = UnitOfWork(db)

    # Crear categoría
    def crear_categoria(self, categoria_data):

        try:

            nueva_categoria = Categoria(
                **categoria_data.model_dump()
            )

            self.repo.create(nueva_categoria)

            self.uow.commit()
            self.db.refresh(nueva_categoria)

            return nueva_categoria

        except Exception as e:
            logger.exception(f"Error creating categoria: {e}")
            self.uow.rollback()
            raise

    # Listar categorías con filtro opcional por parent_id
    def listar_categorias(self, limit: int, offset: int, parent_id=None):

        categorias = self.repo.get_all(parent_id=parent_id)

        return {
            "data": categorias[offset: offset + limit],
            "total": len(categorias)
        }

    # Consulta recursiva: arbol de categorias
    def get_tree(self):
        # Traigo todas las categorias activas
        todas = self.repo.get_all()

        # Construyo el arbol recursivamente
        def _build_tree(parent_id=None):
            tree = []
            for cat in todas:
                if cat.parent_id == parent_id:
                    categoria_data = {
                        "id": cat.id,
                        "nombre": cat.nombre,
                        "descripcion": cat.descripcion,
                        "parent_id": cat.parent_id,
                        "subcategorias": _build_tree(cat.id)
                    }
                    tree.append(categoria_data)
            return tree

        return _build_tree()

    # Obtener categoría por ID
    def obtener_categoria(self, categoria_id: int):

        categoria = self.repo.get_by_id(categoria_id)

        if not categoria:
            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        return categoria

    # Actualizar categoría
    def actualizar_categoria(self, categoria_id: int, datos):

        try:

            categoria = self.repo.get_by_id(categoria_id)

            if not categoria:
                raise HTTPException(
                    status_code=404,
                    detail="Categoria no encontrada"
                )

            update_data = datos.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(categoria, key, value)

            self.repo.update(categoria)

            self.uow.commit()
            self.db.refresh(categoria)

            return categoria

        except Exception as e:
            logger.exception(f"Error updating categoria: {e}")
            self.uow.rollback()
            raise

    # Eliminar categoría (con validacion HTTP 409)
    def eliminar_categoria(self, categoria_id: int):

        try:

            categoria = self.repo.get_by_id(categoria_id)

            if not categoria:
                raise HTTPException(
                    status_code=404,
                    detail="Categoria no encontrada"
                )

            # Verificar si tiene productos activos asociados
            productos_asociados = self.db.exec(
                select(ProductoCategoria).where(
                    ProductoCategoria.categoria_id == categoria_id
                )
            ).first()

            if productos_asociados:
                raise HTTPException(
                    status_code=409,
                    detail="No se puede eliminar la categoria porque tiene productos asociados"
                )

            self.repo.delete(categoria)

            self.uow.commit()

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error deleting categoria: {e}")
            self.uow.rollback()
            raise

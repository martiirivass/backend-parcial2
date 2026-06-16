import logging

from fastapi import HTTPException
from fastapi import UploadFile

from app.models.categoria_model import Categoria

from app.repositories.categoria_repository import (
    CategoriaRepository
)

from app.schemas.common import paginated_response

from app.services.imagen_service import (
    ImagenService
)

logger = logging.getLogger(__name__)


class CategoriaService:

    def __init__(self, db):

        self.db = db

        self.repo = CategoriaRepository(db)

    # Crear categoría
    def crear_categoria(
        self,
        categoria_data
    ):

        nueva_categoria = Categoria(
            **categoria_data.model_dump()
        )

        self.repo.create(
            nueva_categoria
        )

        return nueva_categoria

    # Listar categorías
    def listar_categorias(
        self,
        limit: int,
        offset: int,
        parent_id=None
    ):

        categorias = self.repo.get_all(
            parent_id=parent_id
        )

        return paginated_response(
            categorias[offset: offset + limit],
            len(categorias),
            page=(offset // limit) + 1,
            size=limit,
        )

    # Árbol recursivo
    def get_tree(self):

        todas = self.repo.get_all()

        def _build_tree(parent_id=None):

            tree = []

            for cat in todas:

                if cat.parent_id == parent_id:

                    categoria_data = {
                        "id": cat.id,
                        "nombre": cat.nombre,
                        "descripcion": cat.descripcion,
                        "imagen_url": cat.imagen_url,
                        "parent_id": cat.parent_id,
                        "subcategorias": _build_tree(cat.id)
                    }

                    tree.append(categoria_data)

            return tree

        return _build_tree()

    # Obtener categoría
    def obtener_categoria(
        self,
        categoria_id: int
    ):

        categoria = self.repo.get_by_id(
            categoria_id
        )

        if not categoria:

            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        return categoria

    # Actualizar categoría
    def actualizar_categoria(
        self,
        categoria_id: int,
        datos
    ):

        categoria = self.repo.get_by_id(
            categoria_id
        )

        if not categoria:

            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        update_data = datos.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                categoria,
                key,
                value
            )

        self.repo.update(
            categoria
        )

        return categoria

    # Subir imagen
    def subir_imagen(
        self,
        categoria_id: int,
        archivo: UploadFile
    ):

        categoria = self.repo.get_by_id(
            categoria_id
        )

        if not categoria:

            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        imagen_url = ImagenService.guardar(
            categoria_id,
            archivo
        )

        categoria.imagen_url = imagen_url

        self.repo.update(
            categoria
        )

        return categoria

    # Eliminar categoría
    def eliminar_categoria(
        self,
        categoria_id: int
    ):

        categoria = self.repo.get_by_id(
            categoria_id
        )

        if not categoria:

            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        productos_asociados = (
            self.repo.tiene_productos_asociados(
                categoria_id
            )
        )

        if productos_asociados:

            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar la categoria porque tiene productos asociados"
            )

        self.repo.delete(
            categoria
        )

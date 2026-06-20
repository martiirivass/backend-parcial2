import logging

from fastapi import HTTPException, UploadFile

from app.models.categoria_model import Categoria

from app.repositories.categoria_repository import (
    CategoriaRepository
)

from app.services.imagen_service import (
    ImagenService
)

logger = logging.getLogger(__name__)


class CategoriaService:

    def __init__(self, db):

        self.db = db

        self.repo = CategoriaRepository(db)

    def crear_categoria(
        self,
        categoria_data
    ):
        """Crea una nueva categoría."""

        nueva_categoria = Categoria(
            **categoria_data.model_dump()
        )

        self.repo.create(
            nueva_categoria
        )

        return nueva_categoria

    def listar_categorias(
        self,
        limit,
        offset,
        parent_id=None
    ):
        """Lista las categorías con paginación y filtro opcional por padre."""

        categorias = self.repo.get_all(
            parent_id=parent_id
        )

        total = len(categorias)

        return {
            "data": categorias[offset: offset + limit],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_tree(self):
        """Obtiene el árbol jerárquico de categorías."""
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

    def obtener_categoria(
        self,
        categoria_id: int
    ):
        """Obtiene una categoría por su ID."""
        categoria = self.repo.get_by_id(
            categoria_id
        )

        if not categoria:

            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        return categoria

    def actualizar_categoria(
        self,
        categoria_id: int,
        datos
    ):
        """Actualiza una categoría existente."""

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

    def subir_imagen(
        self,
        categoria_id: int,
        archivo: UploadFile
    ):
        """Sube una imagen de categoría a Cloudinary."""

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

    def eliminar_categoria(
        self,
        categoria_id: int
    ):
        """Elimina una categoría por su ID."""

        categoria = self.repo.get_by_id(
            categoria_id
        )

        if not categoria:

            raise HTTPException(
                status_code=404,
                detail="Categoria no encontrada"
            )

        self.repo.eliminar_asociaciones_productos(
            categoria_id
        )

        self.repo.delete(
            categoria
        )

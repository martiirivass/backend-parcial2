import logging

from fastapi import HTTPException

import cloudinary
import cloudinary.uploader

from app.core.config import (
    settings,
    cloudinary_configurado
)

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class CloudinaryService:

    @classmethod
    def inicializar(cls):
        """Configura el SDK de Cloudinary si hay credenciales."""
        if not cloudinary_configurado():
            logger.warning(
                "Cloudinary no configurado: "
                "faltan CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY o "
                "CLOUDINARY_API_SECRET"
            )
            return False

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

        logger.info(
            "Cloudinary configurado correctamente "
            f"(cloud_name={settings.CLOUDINARY_CLOUD_NAME})"
        )
        return True

    @classmethod
    def subir(
        cls,
        contenido: bytes,
        public_id: str,
        folder: str = "foodstore"
    ) -> dict:
        """
        Sube un archivo a Cloudinary.

        Args:
            contenido: Bytes de la imagen (ya validados)
            public_id: ID público para el archivo en Cloudinary
            folder: Carpeta dentro de Cloudinary (default: 'foodstore')

        Returns:
            Dict con secure_url, public_id, width, height, format, resource_type

        Raises:
            HTTPException 502 si Cloudinary no está disponible
        """
        try:
            resultado = cloudinary.uploader.upload(
                contenido,
                public_id=public_id,
                folder=folder,
                overwrite=False,
                resource_type="image"
            )

            logger.info(
                f"Imagen subida a Cloudinary: {resultado.get('secure_url')}"
            )

            return {
                "secure_url": resultado.get("secure_url"),
                "public_id": resultado.get("public_id"),
                "width": resultado.get("width"),
                "height": resultado.get("height"),
                "format": resultado.get("format"),
                "resource_type": resultado.get("resource_type", "image"),
            }

        except Exception as e:
            logger.error(
                f"Error al subir a Cloudinary: {e}"
            )
            raise HTTPException(
                status_code=502,
                detail=(
                    "Error al subir la imagen a "
                    "Cloudinary. "
                    "Verifique las credenciales "
                    "y la conexión."
                )
            )

    @classmethod
    def eliminar(cls, public_id: str) -> bool:
        """
        Elimina una imagen de Cloudinary por su public_id.

        Args:
            public_id: ID público de la imagen en Cloudinary

        Returns:
            True si se eliminó correctamente

        Raises:
            HTTPException 502 si Cloudinary no está disponible
        """
        try:
            resultado = cloudinary.uploader.destroy(public_id)
            if resultado.get("result") == "ok":
                logger.info(f"Imagen eliminada de Cloudinary: {public_id}")
                return True

            logger.warning(
                f"Cloudinary destroy no retornó ok: {resultado}"
            )
            return False

        except Exception as e:
            logger.error(
                f"Error al eliminar de Cloudinary: {e}"
            )
            raise HTTPException(
                status_code=502,
                detail="Error al eliminar la imagen de Cloudinary"
            )

    @classmethod
    def validar_imagen(cls, contenido: bytes, content_type: str) -> None:
        """Valida tipo MIME y tamaño de una imagen."""
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no soportado: {content_type}. "
                       f"Permitidos: {', '.join(ALLOWED_MIME_TYPES)}"
            )
        if len(contenido) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Máximo 5 MB."
            )

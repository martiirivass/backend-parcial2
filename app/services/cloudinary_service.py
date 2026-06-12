import logging

from fastapi import HTTPException

import cloudinary
import cloudinary.uploader

from app.core.config import (
    settings,
    cloudinary_configurado
)

logger = logging.getLogger(__name__)


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
    ) -> str:
        """
        Sube un archivo a Cloudinary.

        Args:
            contenido: Bytes de la imagen (ya validados)
            public_id: ID público para el archivo en Cloudinary
            folder: Carpeta dentro de Cloudinary (default: 'foodstore')

        Returns:
            URL pública segura (https) de la imagen en Cloudinary

        Raises:
            HTTPException 502 si Cloudinary no está disponible
        """
        try:
            resultado = cloudinary.uploader.upload(
                contenido,
                public_id=public_id,
                folder=folder,
                overwrite=True,
                resource_type="image"
            )

            url = resultado.get("secure_url")

            logger.info(
                f"Imagen subida a Cloudinary: {url}"
            )

            return url

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

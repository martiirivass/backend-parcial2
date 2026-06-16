import logging
import uuid

from pathlib import Path

from fastapi import (
    HTTPException,
    UploadFile
)

from app.core.config import (
    UPLOADS_DIR,
    MAX_IMAGE_SIZE,
    ALLOWED_IMAGE_EXTENSIONS,
    cloudinary_configurado
)

from app.services.cloudinary_service import (
    CloudinaryService
)

logger = logging.getLogger(__name__)


class ImagenService:

    @classmethod
    def validar_extension(
        cls,
        filename: str
    ) -> str:

        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_IMAGE_EXTENSIONS:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Extensión no permitida: "
                    f"{extension}. "
                    f"Use: "
                    f"{', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
                )
            )

        return extension

    @classmethod
    def validar_tamanio(
        cls,
        contenido: bytes
    ):

        if len(contenido) > MAX_IMAGE_SIZE:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La imagen no puede "
                    "superar los 5MB"
                )
            )

    @classmethod
    def generar_nombre(
        cls,
        entidad_id: int,
        extension: str
    ) -> str:

        return (
            f"{entidad_id}_"
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )

    @classmethod
    def guardar(
        cls,
        entidad_id: int,
        archivo: UploadFile
    ) -> str:

        # ── Pre-validación (siempre, antes de cualquier storage) ──
        extension = cls.validar_extension(
            archivo.filename
        )

        contenido = archivo.file.read()

        cls.validar_tamanio(
            contenido
        )

        nombre_archivo = cls.generar_nombre(
            entidad_id,
            extension
        )

        # ── Cloudinary (si configurado) ──
        if cloudinary_configurado():

            resultado = CloudinaryService.subir(
                contenido,
                public_id=nombre_archivo,
                folder="foodstore"
            )

            url = resultado["secure_url"]

            logger.info(
                f"Imagen subida a Cloudinary: {url}"
            )

            return url

        # ── Fallback local ──
        logger.info(
            "Cloudinary no configurado, "
            "usando almacenamiento local"
        )

        UPLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        ruta_archivo = (
            UPLOADS_DIR
            / nombre_archivo
        )

        with open(
            ruta_archivo,
            "wb"
        ) as buffer:

            buffer.write(contenido)

        logger.info(
            f"Imagen guardada localmente: "
            f"{ruta_archivo}"
        )

        return (
            f"/api/v1/uploads/"
            f"{nombre_archivo}"
        )

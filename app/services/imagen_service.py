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
    ALLOWED_IMAGE_EXTENSIONS
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

        extension = cls.validar_extension(
            archivo.filename
        )

        contenido = archivo.file.read()

        cls.validar_tamanio(
            contenido
        )

        UPLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        nombre_archivo = cls.generar_nombre(
            entidad_id,
            extension
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
            f"Imagen guardada correctamente: "
            f"{ruta_archivo}"
        )

        return (
            f"/api/v1/uploads/"
            f"{nombre_archivo}"
        )

import logging
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.models.usuario import Usuario
from app.services.cloudinary_service import CloudinaryService
from app.core.config import cloudinary_configurado

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads Cloudinary"]
)


@router.post(
    "/imagen",
    status_code=201,
    summary="Subir imagen a Cloudinary"
)
def subir_imagen(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(require_roles("ADMIN")),
):
    """
    Sube una imagen a Cloudinary.

    - Valida tipo MIME (jpeg, png, webp)
    - Valida tamaño máximo (5 MB)
    - Devuelve secure_url, public_id, width, height, format, resource_type
    """
    contenido = file.file.read()

    # Validar tipo MIME
    content_type = file.content_type or "application/octet-stream"
    CloudinaryService.validar_imagen(contenido, content_type)

    # Generar public_id único
    extension = _mime_to_extension(content_type)
    public_id = f"{uuid.uuid4().hex}{extension}"

    if cloudinary_configurado():
        resultado = CloudinaryService.subir(
            contenido,
            public_id=public_id,
            folder="foodstore/productos"
        )
    else:
        # Fallback: si Cloudinary no está configurado, devolver error claro
        raise HTTPException(
            status_code=502,
            detail="Cloudinary no está configurado. Configure CLOUDINARY_CLOUD_NAME, "
                   "CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET en el .env"
        )

    return JSONResponse(
        content=resultado,
        status_code=201
    )


@router.delete(
    "/imagen/{public_id:path}",
    status_code=204,
    summary="Eliminar imagen de Cloudinary"
)
def eliminar_imagen(
    public_id: str,
    current_user: Usuario = Depends(require_roles("ADMIN")),
):
    """
    Elimina una imagen de Cloudinary por su public_id.
    """
    if not cloudinary_configurado():
        raise HTTPException(
            status_code=502,
            detail="Cloudinary no está configurado"
        )

    CloudinaryService.eliminar(public_id)

    return None  # 204 No Content


def _mime_to_extension(content_type: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return mapping.get(content_type, ".jpg")

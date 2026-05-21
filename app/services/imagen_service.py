import os
import uuid
import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)

# Extensiones permitidas
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}

# Tamaño máximo: 5MB
MAX_TAMANIO = 5 * 1024 * 1024

# Directorio de uploads
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


def validar_extension(filename: str) -> str:
    """Valida que la extensión del archivo esté permitida.
    
    Args:
        filename: Nombre del archivo original.
    
    Returns:
        La extensión en minúsculas (ej: '.jpg').
    
    Raises:
        HTTPException 400 si la extensión no está permitida.
    """
    ext = Path(filename).suffix.lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida: {ext}. Use: {', '.join(EXTENSIONES_PERMITIDAS)}"
        )
    return ext


def guardar_imagen(producto_id: int, archivo: UploadFile) -> str:
    """Guarda una imagen en el disco y devuelve la URL pública.
    
    Args:
        producto_id: ID del producto asociado.
        archivo: Archivo subido por el usuario.
    
    Returns:
        URL pública de la imagen (ej: '/api/v1/uploads/5_a1b2c3_pizza.jpg').
    
    Raises:
        HTTPException 400 si el archivo es muy grande o extensión inválida.
    """
    # Validar extensión
    ext = validar_extension(archivo.filename)

    # Validar tamaño
    contenido = archivo.file.read()
    if len(contenido) > MAX_TAMANIO:
        raise HTTPException(
            status_code=400,
            detail="La imagen no puede superar los 5MB"
        )

    # Asegurar que el directorio existe
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Generar nombre único: {producto_id}_{uuid_hex}{ext}
    nombre_unico = f"{producto_id}_{uuid.uuid4().hex}{ext}"
    ruta_archivo = UPLOADS_DIR / nombre_unico

    # Guardar archivo
    with open(ruta_archivo, "wb") as f:
        f.write(contenido)

    logger.info(f"Imagen guardada: {ruta_archivo}")

    # Devolver URL pública
    return f"/api/v1/uploads/{nombre_unico}"


def guardar_imagen_categoria(categoria_id: int, archivo: UploadFile) -> str:
    """Guarda la imagen de una categoría (mismo patrón que productos)."""
    return guardar_imagen(categoria_id, archivo)

from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOADS_DIR = BASE_DIR / "uploads"

MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


class Settings(BaseSettings):

    # JWT
    SECRET_KEY: str

    # Mercado Pago
    MP_ACCESS_TOKEN: str | None = None
    MP_PUBLIC_KEY: str | None = None
    MP_NOTIFICATION_URL: str | None = None

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


def cloudinary_configurado() -> bool:
    """Retorna True si todas las credenciales Cloudinary están presentes."""
    return all([
        settings.CLOUDINARY_CLOUD_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ])
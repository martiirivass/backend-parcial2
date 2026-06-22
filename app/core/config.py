from pathlib import Path
from decimal import Decimal

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → raíz del proyecto

UPLOADS_DIR = BASE_DIR / "uploads"

MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

COSTO_ENVIO_DEFAULT = Decimal("50.00")


class Settings(BaseSettings):

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Mercado Pago
    MP_ACCESS_TOKEN: str | None = None
    MP_PUBLIC_KEY: str | None = None
    MP_NOTIFICATION_URL: str | None = None

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174"]'

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # Rate limiting
    REDIS_URL: str = ""
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_REGISTER: str = "5/minute"
    RATE_LIMIT_UPLOAD: str = "5/minute"
    RATE_LIMIT_ADMIN: str = "30/minute"

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
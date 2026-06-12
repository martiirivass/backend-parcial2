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

    # Mercado Pago
    MP_ACCESS_TOKEN: str | None = None
    MP_PUBLIC_KEY: str | None = None
    MP_NOTIFICATION_URL: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
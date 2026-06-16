"""Tests de Uploads: subir y eliminar imágenes (Cloudinary mockeado)."""
from unittest.mock import patch

from fastapi.testclient import TestClient


def _make_test_image() -> tuple[bytes, str]:
    """Retorna contenido PNG mínimo y content-type."""
    return (
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 20,
        "image/png",
    )


class TestSubirImagen:

    @patch("app.routers.uploads_router.CloudinaryService")
    @patch("app.routers.uploads_router.cloudinary_configurado")
    def test_subir_imagen_ok(
        self, mock_config, mock_cloudinary, client, admin_token,
    ):
        """POST /uploads/imagen con admin retorna 201."""
        mock_config.return_value = True
        mock_cloudinary.subir.return_value = {
            "secure_url": "https://res.cloudinary.com/test/image/upload/v1/test.png",
            "public_id": "test.png",
            "width": 100,
            "height": 100,
            "format": "png",
            "resource_type": "image",
        }

        contenido, content_type = _make_test_image()
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.post(
            "/api/v1/uploads/imagen",
            files={"file": ("test.png", contenido, content_type)},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert "secure_url" in data
        assert data["public_id"] == "test.png"

    def test_subir_imagen_sin_auth(self, client):
        """401 sin token."""
        client.cookies.clear()
        contenido, content_type = _make_test_image()
        response = client.post(
            "/api/v1/uploads/imagen",
            files={"file": ("test.png", contenido, content_type)},
        )
        assert response.status_code == 401

    @patch("app.core.config.settings.CLOUDINARY_CLOUD_NAME", "test")
    def test_subir_imagen_mime_invalido(
        self, client, admin_token,
    ):
        """Tipo MIME inválido retorna 400."""
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.post(
            "/api/v1/uploads/imagen",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400

    @patch("app.routers.uploads_router.cloudinary_configurado")
    def test_subir_imagen_sin_cloudinary(
        self, mock_config, client, admin_token,
    ):
        """502 si Cloudinary no está configurado."""
        mock_config.return_value = False

        contenido, content_type = _make_test_image()
        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.post(
            "/api/v1/uploads/imagen",
            files={"file": ("test.png", contenido, content_type)},
        )
        assert response.status_code == 502


class TestEliminarImagen:

    @patch("app.routers.uploads_router.CloudinaryService")
    @patch("app.routers.uploads_router.cloudinary_configurado")
    def test_eliminar_imagen_ok(
        self, mock_config, mock_cloudinary, client, admin_token,
    ):
        """DELETE /uploads/imagen/{public_id} con admin retorna 204."""
        mock_config.return_value = True
        mock_cloudinary.eliminar.return_value = True

        client.cookies.clear()
        client.cookies.set("access_token", admin_token)
        response = client.delete("/api/v1/uploads/imagen/test.png")
        assert response.status_code == 204

    def test_eliminar_imagen_sin_auth(self, client):
        """DELETE sin token retorna 401."""
        client.cookies.clear()
        response = client.delete("/api/v1/uploads/imagen/test.png")
        assert response.status_code == 401

"""Tests básicos con TestClient sobre endpoints públicos y protegidos."""


def test_health_check(client):
    """El endpoint /docs existe y responde (FastAPI docs)."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_listar_productos(client):
    """Endpoint público: GET /api/v1/productos/"""
    response = client.get("/api/v1/productos/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_listar_categorias(client):
    """Endpoint público: GET /api/v1/categorias/"""
    response = client.get("/api/v1/categorias/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_listar_ingredientes(client):
    """Endpoint público: GET /api/v1/ingredientes/"""
    response = client.get("/api/v1/ingredientes/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_listar_unidades_medida(client):
    """Endpoint público: GET /api/v1/unidades-medida/"""
    response = client.get("/api/v1/unidades-medida/")
    assert response.status_code == 200


def test_listar_estados_pedido(client):
    """Endpoint público: GET /api/v1/estados-pedido/"""
    response = client.get("/api/v1/estados-pedido/")
    assert response.status_code == 200


def test_listar_formas_pago(client):
    """Endpoint público: GET /api/v1/formas-pago/"""
    response = client.get("/api/v1/formas-pago/")
    assert response.status_code == 200


def test_auth_register(client):
    """Endpoint público: POST /api/v1/auth/register"""
    import uuid

    email = f"nuevo-{uuid.uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "nombre": "Nuevo",
            "apellido": "Usuario",
            "email": email,
            "password": "Test1234!",
        },
    )
    assert response.status_code == 201


def test_auth_login(client):
    """Endpoint público: POST /api/v1/auth/login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@foodstore.com", "password": "Admin1234!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies



